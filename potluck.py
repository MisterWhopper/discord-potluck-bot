from __future__ import annotations
from dataclasses import dataclass, field
import dateutil.parser as DateParser
from dateutil.parser._parser import ParserError
from datetime import datetime
from pytz import timezone
from typing import Optional, Protocol, Any, Callable
from enum import IntEnum, auto
from functools import partial, wraps

type EventCallback = Callable[[IEvent, NotifierCallback], None]

class DietRestriction(IntEnum):
    VEGAN = auto()
    GLUTEN_FREE = auto()
    KOSHER = auto()
    PESCATARIAN = auto()


class EventType(IntEnum):
    PL_EVENT_CREATE = auto()
    PL_EVENT_EDIT = auto()
    PL_EVENT_DELETE = auto()
    PL_EVENT_ACCEPT_PRECHECK = auto()
    PL_EVENT_DECLINE_PRECHECK = auto()
    PL_EVENT_ACCEPT_POSTCHECK = auto()
    PL_EVENT_DECLINE_POSTCHECK = auto()
    PL_PROFILE_EDIT = auto()


class MessageType(IntEnum):
    USER_NOT_PERMITTED = auto()
    PL_EVENT_CREATED = auto()
    PL_EVENT_NOT_FOUND = auto()



@dataclass
class PLProfile:
    diet_restrictions: DietRestriction
    allergies: list[str]
    strong_dislikes: list[str]


@dataclass
class User:
    id: str
    name: str
    is_mod: bool
    profile: Optional[PLProfile] = None


@dataclass
class Potluck:
    name: str
    event_time: datetime
    location: str
    participants: list[User] = field(default_factory=list)
    announcement_message: Optional[IMessage] = None


@dataclass
class NotifierCallback:
    callback: EventCallback
    notifier: INotifier
    repository: IRepository
    message_factory: IMessageFactory
    settings: Optional[AppSettings] = None


@dataclass
class AppSettings:
    pass


class IMessage(Protocol):
    id: int
    async def resolve(self, data: dict[str, Any]) -> Any: ...


class IMessageFactory(Protocol):
    def build(self, message_type: MessageType, data: Optional[dict[str, Any]]=None): ...


class IEvent(Protocol):
    type: EventType
    from_user: User


def event_of_type(event_type: EventType):
    """
    Helper decorator to ensure IEvent subclasses always have the correct event type associated.
    This is useful for event dispatch
    """
    def decorator(event_cls: IEvent):
        og_new = event_cls.__new__
        def inner(*args, **kwargs):
            inst = og_new(event_cls)
            if inst is not None:
                inst.__init__(*args, **kwargs)
                setattr(inst, "type", event_type)
                return inst
        event_cls.__new__ = inner
        return inner
    return decorator

@event_of_type(EventType.PL_EVENT_CREATE)
@dataclass
class PLEventCreateEvent(IEvent):
    from_user: User
    potluck: Potluck


@event_of_type(EventType.PL_EVENT_EDIT)
@dataclass
class PLEventEditEvent(IEvent):
    from_user: User
    potluck_name: str
    new_potluck: Potluck


@event_of_type(EventType.PL_EVENT_DELETE)
@dataclass
class PLEventDeleteEvent(IEvent):
    from_user: User
    potluck_name: str


class INotifier(Protocol):
    _callbacks: dict[EventType, NotifierCallback]

    def register_callback(self, key: EventType, callback: NotifierCallback) -> None:
        if key in self._callbacks.keys():
            # TODO: Throw error messages properly
            print(f"ERROR: Tried to register a callback for event '{key}' for '{type(self)}', but one already existed")
            return
        self._callbacks[key] = callback

    async def invoke_callback(self, event: IEvent) -> None:
        if event.type not in self._callbacks.keys():
            # TODO: Throw error messages properly
            print(f"ERROR: No callback registered for event '{event.type}' via '{type(self)}'")
            return
        callback_ctx = self._callbacks[event.type]
        await callback_ctx.callback(event, callback_ctx)

    async def send_announcement(message: IMessage): ...
    async def send_message(message: IMessage, to_user: User): ...
    async def update_message(message_id: int, new_message: IMessage): ...
    def run(): ...


class IRepository(Protocol):
    def is_initialized(self) -> bool: ...
    async def init(settings: Optional[AppSettings]) -> None: ...
    async def try_get_user_profile(self, user: User) -> Optional[PLProfile]: ...
    async def try_get_pl_event(self, pl_name: str) -> Optional[Potluck]: ...
    async def save(data: Any): ...



async def on_pl_event_create(event: PLEventCreateEvent, ctx: NotifierCallback):
    if not event.from_user.is_mod:
        await ctx.notifier.send_message(ctx.message_factory.build(MessageType.USER_NOT_PERMITTED), event.from_user)
        return
    await ctx.repository.save(event.potluck) 
    await ctx.notifier.send_announcement(ctx.message_factory.build(MessageType.PL_EVENT_CREATED))

async def on_pl_event_edit(event: PLEventEditEvent, ctx: NotifierCallback):
    """
    1. Retrieve the tracking entry
    1a. Verify the user is either a mod or the organizer of the event themselves
    2. Update the details
    3. Save back to repository
    4. Update previously sent message
    """
    potluck = await ctx.repository.try_get_pl_event(event.pl_name)
    if potluck is None:
        await ctx.notifier.send_message(ctx.message_factory.build(MessageType.PL_EVENT_NOT_FOUND), event.from_user)
    if not (event.from_user == potluck.organizer or event.from_user.is_mod):
        await ctx.notifier.send_message(ctx.message_factory.build(MessageType.USER_NOT_PERMITTED), event.from_user)
    event.new_potluck.announcement_message.id = potluck.announcement_message.id
    await ctx.repository.remove(potluck)
    await ctx.repository.save(event.new_potluck)
    await ctx.notifier.update_message(potluck.announcement_message.id, event.new_potluck)

# NOTE: in discy just call this if either the proper scheduled event or the announcement message are deleted
async def on_pl_event_delete(event: PLEventDeleteEvent, ctx: NotifierCallback):

    pass

async def on_pl_event_accept_precheck(event: IEvent, ctx: NotifierCallback):
    """
    1. Check to see if user has already set up a profile
        1a. if not, then maybe we decline the interaction until they do it?
    2. Send user a message prompting them for their contribution
    """
    pass

async def on_pl_event_decline_precheck(event: IEvent, ctx: NotifierCallback):
    pass

async def on_pl_event_accept_postcheck(event: IEvent, ctx: NotifierCallback):
    """
    1. Retrive tracking entry
    2. Add user as a participant
    3. Recalc required items based on contribution
    4. Update health considerations if necessary
    5. Update & save tracking entry
    6. Update announcement message
    """
    pass

async def on_pl_event_decline_postcheck(event: IEvent, ctx: NotifierCallback):
    pass

async def on_pl_profile_edit(event: IEvent, ctx: NotifierCallback):
    """
    1. Check if user ever created a profile (if not, create it)
    2. Update w/ new user parms & save to repo
    """
    pass

def start_pl_bot(notifier: INotifier, repository: IRepository, message_factory: IMessageFactory, settings: Optional[AppSettings] = None):
    """
    Operations as follows:
        1. Intitialize the repository if necessary
        2. register all event callbacks
        3. pass control to notifier.run()
    """
    if not repository.is_initialized():
        repository.init(settings)
    callback_builder = partial(NotifierCallback, notifier=notifier,repository=repository, message_factory=message_factory, settings=settings)
    notifier.register_callback(EventType.PL_EVENT_CREATE, callback_builder(on_pl_event_create))
    notifier.register_callback(EventType.PL_EVENT_EDIT, callback_builder(on_pl_event_edit))
    notifier.register_callback(EventType.PL_EVENT_DELETE, callback_builder(on_pl_event_delete))
    notifier.register_callback(EventType.PL_EVENT_ACCEPT_PRECHECK, callback_builder(on_pl_event_accept_precheck))
    notifier.register_callback(EventType.PL_EVENT_DECLINE_PRECHECK, callback_builder(on_pl_event_decline_precheck))
    notifier.register_callback(EventType.PL_EVENT_ACCEPT_POSTCHECK, callback_builder(on_pl_event_accept_postcheck))
    notifier.register_callback(EventType.PL_EVENT_DECLINE_POSTCHECK, callback_builder(on_pl_event_decline_postcheck))
    notifier.register_callback(EventType.PL_PROFILE_EDIT, callback_builder(on_pl_profile_edit))
    notifier.run()

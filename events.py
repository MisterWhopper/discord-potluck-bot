from potluck import NotifierCallback, User, Potluck
from typing import Callable, Protocol
from enum import IntEnum, auto
from dataclasses import dataclass
from functools import wraps, dataclass_transform

type EventCallback = Callable[[IEvent, NotifierCallback], None]

class EventType(IntEnum):
    PL_EVENT_CREATE = auto()
    PL_EVENT_EDIT = auto()
    PL_EVENT_DELETE = auto()
    PL_EVENT_ACCEPT_PRECHECK = auto()
    PL_EVENT_DECLINE_PRECHECK = auto()
    PL_EVENT_ACCEPT_POSTCHECK = auto()
    PL_EVENT_DECLINE_POSTCHECK = auto()
    PL_PROFILE_EDIT = auto()


class IEvent(Protocol):
    type: EventType
    from_user: User


class EventListener:
    def __init__(self):
        self.callbacks: dict[EventType, EventCallback] = {}

    def register(self, event_type: EventType, callback: EventCallback) -> None:
        if event_type in self.callbacks.keys():
            # TODO: Throw error messages properly
            print(f"ERROR: Tried to register a callback for event '{event_type}' for '{type(self)}', but one already existed")
            return
        self.callbacks[event_type] = callback

    async def invoke_callback(self, event: IEvent) -> None:
        if event.type not in self.callbacks.keys():
            # TODO: Throw error messages properly
            print(f"ERROR: No callback registered for event '{event.type}' via '{type(self)}'")
            return
        if (callback_ctx := self.callbacks.get(event.type)) is not None:
            await callback_ctx(event, callback_ctx)


@dataclass_transform
def event_of_type(event_type: EventType):
    """
    Helper decorator to ensure IEvent subclasses always have the correct event type associated.
    This is useful for event dispatch
    """
    def decorator(event_cls: IEvent):
        og_new = event_cls.__new__
        @wraps(event_cls)
        def inner(*args, **kwargs):
            inst = og_new(event_cls)
            if inst is not None:
                inst.__init__(*args, **kwargs)
                setattr(inst, "type", event_type)
                return inst
        event_cls.__new__ = inner
        event_cls = dataclass(event_cls)
        return inner
    return decorator

@event_of_type(EventType.PL_EVENT_CREATE)
class PLEventCreateEvent(IEvent):
    from_user: User
    potluck: Potluck


@event_of_type(EventType.PL_EVENT_EDIT)
class PLEventEditEvent(IEvent):
    from_user: User
    potluck_name: str
    new_potluck: Potluck


@event_of_type(EventType.PL_EVENT_DELETE)
class PLEventDeleteEvent(IEvent):
    from_user: User
    potluck_name: str



from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol, Any
from enum import IntEnum, auto
from functools import partial
from events import *

class ItemType(IntEnum):
    ENTREE = auto()
    SIDE = auto()
    BEVERAGE = auto()
    DESSERT = auto()
    MISC = auto()


class DietRestriction(IntEnum):
    VEGAN = 1 << 0
    GLUTEN_FREE = 1 << 1
    KOSHER = 1 << 2
    PESCATARIAN = 1 << 3


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
class ItemCommitment:
    potluck_name: str
    from_user: User
    item_name: str
    item_type: ItemType
    # Default to assuming an item is not safe for any diet restriction
    friendly_diets: DietRestriction = 0


@dataclass
class ItemRequirement:
    item_type: ItemType
    quantity: int
    diet_requirements: DietRestriction = 0

    @staticmethod
    def default() -> list[ItemRequirement]:
        """
        Returns the default 'starting' item requirements for a brand-new potluck
        """
        return [ItemRequirement(ItemType.ENTREE, 1), ItemRequirement(ItemType.SIDE, 2), ItemRequirement(ItemType.BEVERAGE, 1), ItemRequirement(ItemType.MISC, 0)]

@dataclass
class Potluck:
    name: str
    event_time: datetime
    location: str
    participants: list[User] = field(default_factory=list)
    item_requirements: list[ItemRequirement] = ItemRequirement.default()
    item_commitments: list[ItemCommitment] = field(default_factory=list)
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
    def build(
        self, message_type: MessageType, data: Optional[dict[str, Any]] = None
    ) -> IMessage: ...


class INotifier(Protocol):
    def forward_event_registration(
        self, event_type: EventType, callback: NotifierCallback
    ) -> None: ...
    async def send_announcement(self, message: IMessage): ...
    async def send_message(self, message: IMessage, to_user: User): ...
    async def update_message(self, message_id: int, new_message: IMessage): ...
    def run(self): ...


class IRepository(Protocol):
    def is_initialized(self) -> bool: ...
    def init(self, settings: Optional[AppSettings]) -> None: ...
    async def try_get_user_profile(self, user: User) -> Optional[PLProfile]: ...
    async def try_get_pl_event(self, pl_name: str) -> Optional[Potluck]: ...
    async def save(self, data: Any): ...



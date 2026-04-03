from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol
from string import Template

@dataclass
class Participant:
    name: str
    allergies: list[str]
    diet: list[str]


@dataclass 
class Item:
    name: str
    quantity: int


class IMessage(Protocol):
    message_template: Template
    def resolve(variables: Any) -> str: ...


@dataclass
class PotluckCreatedMessage(IMessage):
    
    message_template: Template
    pass


@dataclass
class Potluck:
    participants: list[Participant] = field(default_factory=list)
    items_required: list[Item] = field(default_factory=list)


class IEventRecorder(Protocol):
    def add_event(self, potluck: Potluck) -> None: ...


# NOTE: This is technically unnecessary to the stated goal of tracking potluck items
#       ...that said, it'd be nice to know if an item contains a dangerous ingredient.
class IItemAuditor(Protocol):
    def check_allergies(self, potluck: Potluck) -> list[str]: ...


class INotifier(Protocol):
    event_recorder: IEventRecorder
    def send_message(self, message: IMessage): ...

class PotluckEvent:
    def __init__(self, potluck: Potluck):
        self.potluck = potluck

    @staticmethod
    def create(potluck: Potluck, notifier: INotifier) -> PotluckEvent:
        # Should post a message saying that a potluck has been created
        notifier.send_message()
        return PotluckEvent(potluck)
        

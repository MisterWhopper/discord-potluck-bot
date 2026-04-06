from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import re

ITEM_PARSING_PATTERN = re.compile(r"(?:\s*[-*])?(\d+(?=x)){1}x\s*(.*)")


@dataclass 
class Item:
    name: str
    quantity: int
    assignees: Optional[list[str]] = None


@dataclass
class PotluckEvent:
    name: str
    items_required: list[Item] = field(default_factory=list)


@dataclass
class PotluckOrganizer:
    active_potlucks: dict[str, PotluckEvent] = field(default_factory=dict)

    def update(self, potluck: PotluckEvent):
        self.active_potlucks[potluck.name] = potluck

    def get_unassigned_items(self, potluck_name: str) -> Optional[list[Item]]:
        if potluck_name not in self.active_potlucks:
            return None
        unassigned_items = [i for i in self.active_potlucks[potluck_name].items_required if i.assignees is None]
        return unassigned_items

def parse_items(items_raw_str: str) -> list[Item]:
    results: list[Item] = []
    if (items := ITEM_PARSING_PATTERN.findall(items_raw_str)) is not None:
        for item_details in items:
            item_quantity, item_name = item_details
            try:
                results.append(Item(item_name, int(item_quantity)))
            except ValueError:
                print(f"WARNING: Could not parse an int from '{item_quantity}'")
                continue
    return results

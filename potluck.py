from __future__ import annotations
from dataclasses import dataclass, field
import dateutil.parser as DateParser
from dateutil.parser._parser import ParserError
from datetime import datetime
from pytz import timezone
from typing import Optional
import re

ITEM_PARSING_PATTERN = re.compile(r"(?:\s*[-*])?(\d+(?=x)){1}x\s*(.*)")

CURRENT_TIMEZONE = timezone("US/Central")

@dataclass 
class Item:
    name: str
    quantity: int
    assignees: Optional[list[str]] = field(default_factory=list)


@dataclass
class PotluckEvent:
    name: str
    event_time: datetime
    location: str
    items_required: list[Item] = field(default_factory=list)


@dataclass
class PotluckOrganizer:
    active_potlucks: dict[str, PotluckEvent] = field(default_factory=dict)

    def update(self, potluck: PotluckEvent):
        self.active_potlucks[potluck.name] = potluck

    def get_unassigned_items(self, potluck_name: str) -> Optional[list[Item]]:
        if potluck_name not in self.active_potlucks:
            return None
        unassigned_items = [i for i in self.active_potlucks[potluck_name].items_required if len(i.assignees) == 0]
        return unassigned_items

    def claim_item(self, item_key: str, user_name: str):
        potluck_name = item_key.split('.')[0]
        item_name = item_key.split('.')[1]
        if potluck_name not in self.active_potlucks:
            return
        item = next(iter([i for i in self.active_potlucks[potluck_name].items_required if i.name == item_name]))
        item.assignees.append(user_name)
        # item_idx = self.active_potlucks[potluck_name].items_required.index(item_name, key=lambda i:i.name)
        # self.active_potlucks[potluck_name].items_required[item_idx].assigness.append(user_name)


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

def try_parse_datetime(timestamp: str) -> Optional[datetime]:
    try:
        result = DateParser.parse(timestamp, fuzzy=True)
        # The resulting datetime object must be timezone-aware for Discord to work
        if result.tzinfo is None or result.tzinfo.utcoffset(result) is None:
            # Assume it's the local timezone
            # FIXME: Could there be a way to prompt the user for their timezone? 
           result = CURRENT_TIMEZONE.localize(result) 
        return result
    except ParserError:
        return None

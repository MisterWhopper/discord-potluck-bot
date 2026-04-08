import discord
from discord import app_commands
from datetime import datetime
import dateutil.parser as DateParser
from dateutil.parser._parser import ParserError
from typing import Optional
from pytz import timezone
from ui import CreatePotluckModal, ClaimPotluckItemModal, organizer, PotluckEventView
# from potluck import Item, parse_items, PotluckEvent, PotluckOrganizer

CURRENT_TIMEZONE = timezone("US/Central")
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

class PotluckBot(discord.Client):
    user: discord.ClientUser

    def __init__(self, enabled_guilds=[]) -> None:
        intents = discord.Intents.default()
        # intents.message_content = True
        super().__init__(intents = intents)

        # Need a CommandTree for commands to work at all
        self.tree = app_commands.CommandTree(self)
        self.enabled_guilds = enabled_guilds

    
    async def on_ready(self):
        print("Bot connected successfully")
    
    async def setup_hook(self) -> None:
        for g in self.enabled_guilds:
            self.tree.copy_global_to(guild=g)
            await self.tree.sync(guild=g)


async def potluck_create_impl(client: discord.ClientUser, interaction: discord.Interaction):
    await interaction.response.send_modal(CreatePotluckModal())

async def potluck_claim_item_impl(client: discord.ClientUser, interaction: discord.Interaction, potluck_name: str):
    item_modal = ClaimPotluckItemModal()
    item_modal.add_potluck_items(potluck_name)
    await interaction.response.send_modal(item_modal)


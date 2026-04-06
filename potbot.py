import discord
from discord import app_commands
from ui import CreatePotluckModal, ClaimPotluckItemModal, organizer
# from potluck import Item, parse_items, PotluckEvent, PotluckOrganizer


class PotluckBot(discord.Client):
    user: discord.ClientUser

    def __init__(self, enabled_guilds=[]) -> None:
        intents = discord.Intents.default()
        # intents.message_content = True
        super().__init__(intents = intents)

        # Need a CommandTree for commands to work at all
        self.tree = app_commands.CommandTree(self)
        self.enabled_guilds = enabled_guilds.copy()

    
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


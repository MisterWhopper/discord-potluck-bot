from __future__ import annotations
import discord
import traceback
from datetime import timedelta
from potluck import Item, PotluckOrganizer, parse_items, PotluckEvent, try_parse_datetime
# from potbot import create_potluck_on_submit_impl, claim_potluck_on_submit_impl

organizer = PotluckOrganizer()


class CreatePotluckModal(discord.ui.Modal, title='Create Potluck'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    event_name = discord.ui.TextInput(
        label='Event Name',
        placeholder='Same old thing we did last week',
    )

    event_description = discord.ui.TextInput(
        label='Description',
        style=discord.TextStyle.long,
        required=False,
        max_length=300
    )

    event_date = discord.ui.TextInput(
        label='Date & Time',
        placeholder='1999/12/31 11:59 PM',
    )
    event_location = discord.ui.TextInput(
        label="Location",
        placeholder="ur mom's house"
    )
    # items_to_bring = discord.ui.TextInput(
    #     label='Additional items still needed',
    #     style=discord.TextStyle.long,
    #     placeholder='Format: <quantity>x <item> (one entry per line)',
    #     required=False,
    #     max_length=300,
    # )

    async def on_submit(self, interaction: discord.Interaction):
        await create_potluck_on_submit_impl(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class PotluckEventView(discord.ui.LayoutView):
    message: discord.Message | None = None
    container = discord.ui.Container["PotluckEventView"](
        discord.ui.Section(
            "## Test button", 
            "Click on the button to create a modal",
            accessory=discord.ui.Thumbnail["PotluckEventView"]("https://i.imgur.com/9sDnoUW.jpeg")
        ),
        accent_color=discord.Color.blurple(),
    )
    row: discord.ui.ActionRow[PotluckEventView] = discord.ui.ActionRow()

    # TODO: This is where an interaction_check method would go

    @row.button(label="Click me", style=discord.ButtonStyle.green)
    async def callback(self, interaction: discord.Interaction, button):
        print("Button was clicked!")
        await interaction.response.send_modal(CreatePotluckModal())


class SelectWithCallback(discord.ui.Select):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def callback(interaction: discord.Interaction):
        print(f"callback: {interaction = }")

    async def interaction_check(interaction: discord.Interaction):
        print(f"interaction_check: {interaction}")

class ClaimPotluckItemModal(discord.ui.Modal, title='Claim Potluck item'):
    items_available_label = discord.ui.Label(
        text="Please select an item below",
        description="Unselected items",
        component=SelectWithCallback(
            #max_values=25,
            required=True,
        )
    )

    def add_potluck_items(self, potluck_name: str):
        unassigned_items = organizer.get_unassigned_items(potluck_name)
        for item in unassigned_items:
            print(f"Trying to add item '{item}'... ")
            self.items_available_label.component.add_option(label=f"{item.quantity}x {item.name}",value=f"{potluck_name}.{item.name}",default=False)

    async def on_submit(self, interaction: discord.Interaction):
        await claim_potluck_on_submit_impl(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


async def claim_potluck_on_submit_impl(modal: ClaimPotluckItemModal, interaction: discord.Interaction):
        item_claimed = modal.items_available_label.component.values[0]
        organizer.claim_item(item_claimed, interaction.user.name)
        await interaction.response.send_message(f"Item '{item_claimed}' has been claimed!", ephemeral=True)

async def create_potluck_on_submit_impl(modal: CreatePotluckModal, interaction: discord.Interaction):
        potluck_name = modal.event_name.value
        description = modal.event_description.value
        location = modal.event_location.value
        timestamp = try_parse_datetime(modal.event_date.value)
        if timestamp is None:
            await interaction.response.send_message(f"Error: Could not understand timestamp input '{timestamp}', please try again.")
            return
        # Just set the end time by default to the end of the suggested day
        to_eod = timedelta(hours=23-timestamp.hour, minutes=59-timestamp.minute, seconds=59-timestamp.minute)
        end_time = timestamp + to_eod
        # items = parse_items(modal.items_to_bring.value)
        potluck = PotluckEvent(potluck_name, timestamp, location, [])
        organizer.update(potluck)
        print(organizer.active_potlucks)
        # Create a scheduled event in Discord (hey the feature exists, may as well use it
        await interaction.guild.create_scheduled_event(name=potluck_name, start_time=timestamp,location=location,description=description, end_time=end_time, entity_type=discord.EntityType.external, privacy_level=discord.PrivacyLevel.guild_only)
        await interaction.response.send_message(f'Enjoy the cookout, {interaction.user.display_name}!', ephemeral=True)

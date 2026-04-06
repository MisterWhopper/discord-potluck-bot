import discord
import traceback
from potluck import Item, PotluckOrganizer, parse_items, PotluckEvent
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

    # This is a longer, paragraph style input, where user can submit feedback
    # Unlike the name, it is not required. If filled out, however, it will
    # only accept a maximum of 300 characters, as denoted by the
    # `max_length=300` kwarg.
    items_to_bring = discord.ui.TextInput(
        label='Items for purchase',
        style=discord.TextStyle.long,
        placeholder='Format: - <quantity>x <item>',
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_potluck_on_submit_impl(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

class ClaimPotluckItemModal(discord.ui.Modal, title='Claim Potluck item'):

    items_available_label = discord.ui.Label(
        text="Please select an item below",
        description="Unselected items",
        component=discord.ui.Select(
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
        items = parse_items(modal.items_to_bring.value)
        potluck = PotluckEvent(potluck_name, items)
        organizer.update(potluck)
        print(organizer.active_potlucks)
        await interaction.response.send_message(f'Enjoy the cookout, {modal.event_name.value}!', ephemeral=True)

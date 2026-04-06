import discord
import traceback
from potluck import parse_items


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
        # print(f"{interaction = }\n{dir(interaction) = }\n{interaction.original_response = }")
        # print(self.description)
        await create_potluck_on_submit_impl(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)

class ClaimPotluckItemModal(discord.ui.Modal, title='Claim Potluck item'):
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
        await on_submit_impl(self, interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


async def on_submit_impl(modal: CreatePotluckModal, interaction: discord.Interaction):
        await interaction.response.send_message(f'Enjoy the cookout, {modal.name.value}!', ephemeral=True)

async def create_potluck_on_submit_impl(modal: CreatePotluckModal, interaction: discord.Interaction):
        parse_items(modal.items_to_bring.value)
        await interaction.response.send_message(f'Enjoy the cookout, {modal.event_name.value}!', ephemeral=True)

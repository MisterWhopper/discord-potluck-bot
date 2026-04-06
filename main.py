from potbot import PotluckBot, potluck_create_impl, potluck_claim_item_impl
import discord
from discord import app_commands
import os

client = PotluckBot(enabled_guilds=[discord.Object(id=865824431472377867)])

def get_token() -> str:
    return os.environ.get("DISCORD_TOKEN", "")

TOKEN = get_token()

@client.tree.command(name="pot_create",description="Potluck test")
async def potluck(interaction: discord.Interaction):
    await potluck_create_impl(client, interaction)

@client.tree.command(name="pot_claim",description="Claim item in potluck")
@app_commands.describe(potluck_name="Name of Potluck event")
async def potluck_claim(interaction: discord.Interaction, potluck_name: str):
    await potluck_claim_item_impl(client, interaction, potluck_name)


def main():
    print("Hello from discord-potluck-bot!")
    client.run(TOKEN)

if __name__ == "__main__":
    main()

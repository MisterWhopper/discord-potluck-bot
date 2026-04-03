from potbot import PotluckBot, potluck_create_impl
import discord
import os

client = PotluckBot(enabled_guilds=[discord.Object(id=865824431472377867)])

def get_token() -> str:
    return os.environ.get("DISCORD_TOKEN", "")

TOKEN = get_token()

@client.tree.command(name="potluck",description="Potluck test")
async def potluck(interaction: discord.Interaction):
    await potluck_create_impl(client, interaction)

def main():
    print("Hello from discord-potluck-bot!")
    client.run(TOKEN)

if __name__ == "__main__":
    main()

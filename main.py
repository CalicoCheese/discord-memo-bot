import discord
import client
from config.config import get_config
from utils.directory import directory

if __name__ == "__main__":
    parser = get_config()
    token = parser.get("DEFAULT", "discord-token")

    client = client.Client(
        intents=discord.Intents.default()
    )
    client.load_extensions('listeners', directory)
    client.run(token)

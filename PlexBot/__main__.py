"""
Main entrypoint script.
Sets up loggers and initiates bot.
"""
import logging
import asyncio

import discord
from discord.ext.commands import Bot

from . import load_config
from .bot import General
from .bot import Plex

# Load config from file
configdir = "config"
from os import geteuid
if geteuid() == 0:
    configdir = "/config"
config = load_config(configdir,"config.yaml")

BOT_PREFIX = config["discord"]["prefix"]
TOKEN = config["discord"]["token"]

BASE_URL = config["plex"]["base_url"]
PLEX_TOKEN = config["plex"]["token"]
LIBRARY_NAME = config["plex"]["library_name"]

if config["lyrics"]:
    LYRICS_TOKEN = config["lyrics"]["token"]
else:
    LYRICS_TOKEN = None
    
# Set appropiate log level
root_log = logging.getLogger()
plex_log = logging.getLogger("Plex")
bot_log = logging.getLogger("Bot")

plex_log.setLevel(config["plex"]["log_level"])
bot_log.setLevel(config["discord"]["log_level"])

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.voice_states = True
intents.reactions = True

plex_args = {
    "base_url": BASE_URL,
    "plex_token": PLEX_TOKEN,
    "lib_name": LIBRARY_NAME,
    "lyrics_token": LYRICS_TOKEN,
}

bot = Bot(command_prefix=BOT_PREFIX, intents=intents)
# Remove help command, we have our own custom one.
bot.remove_command("help")
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    await bot.tree.sync()  # Sync application commands here

async def start_audio_player_task():
    await bot.cogs['Plex']._audio_player_task()

async def main():
    await bot.add_cog(Plex(bot, **plex_args))
    await bot.start(TOKEN)

asyncio.run(main())

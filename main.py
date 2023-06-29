import discord
import logging
import os
from dotenv import load_dotenv

from bot import Chiffon

# setup a logger for discord.py
logging.basicConfig(level=logging.INFO)

# load environment variables from .env
load_dotenv(verbose=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# variables
TOKEN = os.getenv("TOKEN")
PREFIX = "."

if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.typing = False
    intents.message_content = True
    client = Chiffon(PREFIX, intents=intents, status=discord.Status.idle)
    client.run(TOKEN)

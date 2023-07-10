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

# :3
art = """
   ______  __        _     ___    ___                  
 .' ___  |[  |      (_)  .' ..] .' ..]                 
/ .'   \_| | |--.   __  _| |_  _| |_   .--.   _ .--.   
| |        | .-. | [  |'-| |-''-| |-'/ .'`\ \[ `.-. |  
\ `.___.'\ | | | |  | |  | |    | |  | \__. | | | | |  
 `.____ .'[___]|__][___][___]  [___]  '.__.' [___||__]                                         
"""

if __name__ == '__main__':
    print(art)
    intents = discord.Intents.default()
    intents.typing = False
    intents.message_content = True
    client = Chiffon(PREFIX, intents=intents, status=discord.Status.idle)
    client.run(TOKEN)

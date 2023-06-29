import aiohttp
import discord
from discord.ext import commands
from discord.ext import tasks

import settings


class Chiffon(commands.Bot):
    def __init__(self, prefix: str, status: discord.Status, intents: discord.Intents) -> None:
        super().__init__(prefix, status=status, intents=intents)
        self.aiohttp_session = None
        self.compatibility = {}
        self.plugins = {}
        self.plugin_names = {}  # [lowercase name : real name] for a search
        self.remove_command("help")  # remove a default help command

    async def on_ready(self) -> None:
        print(f"[*] Logged in as {self.user}")
        # initialize database
        self.aiohttp_session = aiohttp.ClientSession(loop=self.loop)
        self.update_compatibility_list.start()
        await self.update_addon_list()
        # load cogs
        await self.load_extension("addons")
        await self.load_extension("developer")
        # sync commands
        await self.tree.sync()
        # print([f"<:{e.name}:{e.id}>" for e in self.get_guild(1123260961931927672).emojis])

    @tasks.loop(hours=24)
    async def update_compatibility_list(self):
        resp = await self.aiohttp_session.get(settings.compatibility_url)
        data = await resp.json(content_type=None)
        self.compatibility = data

    async def update_addon_list(self):
        resp = await self.aiohttp_session.get(settings.plugins_url)
        data = await resp.json(content_type=None)
        self.plugins = data
        self.plugin_names = {name.lower(): name for name in self.plugins.keys()}

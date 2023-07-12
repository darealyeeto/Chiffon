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
        self.themes = {}
        self.remove_command("help")  # remove a default help command

    async def on_ready(self) -> None:
        print(f"[*] Logged in as {self.user}")
        # initialize database
        self.aiohttp_session = aiohttp.ClientSession(loop=self.loop)
        # start a loop task for fetching updates of the compatibility list
        if not self.update_compatibility_list.is_running():
            self.update_compatibility_list.start()
            await self.update_plugin_list()
            await self.update_theme_list()
        # load cogs
        await self.load_extension("addon")
        await self.load_extension("developer")
        # sync commands
        await self.tree.sync()
        # DEBUG: dump emojis
        # print([f"<:{e.name}:{e.id}>" for e in self.get_guild(settings.chiffon_guild).emojis])

    @tasks.loop(hours=24)
    async def update_compatibility_list(self) -> None:
        resp = await self.aiohttp_session.get(settings.compatibility_url)
        data = await resp.json(content_type=None)
        self.compatibility = data

    async def update_plugin_list(self) -> None:
        resp = await self.aiohttp_session.get(settings.plugins_url)
        data = await resp.json(content_type=None)
        self.plugins = data

    async def update_theme_list(self) -> None:
        resp = await self.aiohttp_session.get(settings.themes_url)
        data = await resp.json(content_type=None)
        self.themes = data

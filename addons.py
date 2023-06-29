import json
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

from bot import Chiffon
import settings


class Addons(commands.Cog):

    def __init__(self, bot: Chiffon) -> None:
        self.bot = bot

    def build_plugin_embed(self, plugin_name):
        plugin = self.bot.plugins[plugin_name]
        # build an embed
        color_hex = "#524FBF" if "color" not in plugin else plugin["color"]
        color = discord.Color.from_str(color_hex)
        embed = discord.Embed(color=color)
        embed.title = plugin_name
        if "description" in plugin:
            embed.description = plugin["description"]
        if "version" in plugin:
            embed.add_field(name="Version", value=plugin["version"])
        if "author" in plugin:
            try:
                author = json.loads(plugin["author"])
            except json.decoder.JSONDecodeError:
                pass
            else:
                embed.add_field(name="Author", value=", ".join([a["name"] for a in author]))
        if plugin_name in self.bot.compatibility["plugin"].keys():
            note = self.bot.compatibility["plugin"][plugin_name]
            if "~" in note["ver"]:
                embed.add_field(name="Compatible with", value=note["ver"])
                embed.add_field(name="Compatibility Note", value=note["text"])
            elif note["ver"] in ["Unknown", "Not Recommended"]:
                embed.add_field(name="Warning", value=note["text"])
            elif note["ver"] == "Working":
                embed.add_field(name="Note", value=note["text"])
        # add a button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Install plugin", url=settings.plugin_install_scheme % (plugin["url"])))  # url only accepts one of ('http', 'https', 'discord')
        return {"embed": embed, "view": view}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # detect changes of the database
        if message.channel.id == settings.addon_update_channel:
            await self.bot.update_addon_list()

        # react to [[AddonName]]
        elif message.content.startswith("[[") and message.content.endswith("]]"):
            # parse the provided name
            provided_name = message.content.lstrip("[[").rstrip("]]")
            provided_name = provided_name.replace("_", "").replace(" ", "").lower()  # normalize the provided name
            if provided_name not in self.bot.plugin_names:
                return
            plugin_name = self.bot.plugin_names[provided_name]
            ret = self.build_plugin_embed(plugin_name)
            await message.reply(**ret)

    @app_commands.command(name="search", description="search plugins")
    async def search(self, interaction: discord.Interaction, plugin_name: str) -> None:
        ret = self.build_plugin_embed(plugin_name)
        await interaction.response.send_message(**ret)

    @search.autocomplete("plugin_name")
    async def search_autocomplete(self, interaction: discord.Interaction, query: str) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=name, value=name) for name in self.bot.plugins.keys() if query.lower() in name.lower()]


async def setup(bot: Chiffon):
    await bot.add_cog(Addons(bot))

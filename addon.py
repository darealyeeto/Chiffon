import json
from typing import List

import discord
from discord import app_commands
from discord.ext import commands

import response
from bot import Chiffon
import settings


class Addon(commands.Cog):

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
            embed.add_field(name="Author", value=", ".join([a["name"] for a in plugin["author"]]))
        if "last_update" in plugin:
            embed.add_field(name="Last Updated Date", value=f"<t:{plugin['last_update']}:d> (<t:{plugin['last_update']}:R>)")
        alt = ""
        if plugin_name in self.bot.compatibility["plugin"].keys():
            note = self.bot.compatibility["plugin"][plugin_name]
            if "~" in note["ver"]:
                if "alt" in note:
                    note["text"] = note["text"].replace("\n" + note["alt"], "")
                    alt = note["alt"]
                embed.add_field(name="Compatible with", value=note["ver"])
                embed.add_field(name="Compatibility Notes", value=note["text"], inline=False)
            elif note["ver"] in ["Unknown", "Not Recommended"]:
                embed.add_field(name="Warning", value=note["text"], inline=False)
            elif note["ver"] == "Working":
                embed.add_field(name="Notes", value=note["text"], inline=False)
        # add a button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Install plugin", url=settings.plugin_install_scheme % (plugin["url"])))  # url only accepts one of ('http', 'https', 'discord')
        if alt:
            view.add_item(discord.ui.Button(label="Install fixed version [Recommended]", url=settings.plugin_install_scheme % alt))
        if "message_id" in plugin:
            view.add_item(discord.ui.Button(label="Original post", url=settings.message_link % (settings.plugins_channel, plugin["message_id"])))
        return {"embed": embed, "view": view}

    def build_theme_embed(self, theme_name):
        theme = self.bot.themes[theme_name]
        # build an embed
        color_hex = "#524FBF" if "color" not in theme else theme["color"]
        color = discord.Color.from_str(color_hex)
        embed = discord.Embed(color=color)
        embed.title = theme_name
        if "description" in theme:
            embed.description = theme["description"]
        if "version" in theme:
            embed.add_field(name="Version", value=theme["version"])
        if "author" in theme:
            embed.add_field(name="Author", value=", ".join([a["name"] for a in theme["author"]]))
        # add a button
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Install theme", url=settings.theme_install_scheme % (theme["url"])))  # url only accepts one of ('http', 'https', 'discord')
        if "message_id" in theme:
            view.add_item(discord.ui.Button(label="Original post", url=settings.message_link % (settings.themes_channel, theme["message_id"])))
        return {"embed": embed, "view": view}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # detect changes of the database
        if message.channel.id == settings.plugin_update_channel:
            await self.bot.update_plugin_list()
        elif message.channel.id == settings.theme_update_channel:
            await self.bot.update_theme_list()

        # react to [[AddonName]]
        elif message.content.startswith("[[") and message.content.endswith("]]"):
            # parse the provided name
            provided_name = message.content.lstrip("[[").rstrip("]]")
            provided_name = provided_name.replace("_", "").replace(" ", "").lower()  # normalize the provided name
            if provided_name in self.bot.plugin_names:
                plugin_name = self.bot.plugin_names[provided_name]
                ret = self.build_plugin_embed(plugin_name)
                await message.reply(**ret)
            elif provided_name in self.bot.theme_names:
                theme_name = self.bot.theme_names[provided_name]
                ret = self.build_theme_embed(theme_name)
                await message.reply(**ret)

    @app_commands.command(name="plugin", description="search plugins")
    async def plugin(self, interaction: discord.Interaction, name: str) -> None:
        if name not in self.bot.plugins.keys():
            await interaction.response.send_message(embed=response.error("Please enter a valid plugin name"))
            return
        ret = self.build_plugin_embed(name)
        await interaction.response.send_message(**ret)

    @plugin.autocomplete("name")
    async def plugin_autocomplete(self, interaction: discord.Interaction, query: str) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=name, value=name) for name in self.bot.plugins.keys() if query.lower() in name.lower()][:25]

    @app_commands.command(name="theme", description="search themes")
    async def theme(self, interaction: discord.Interaction, name: str) -> None:
        if name not in self.bot.themes.keys():
            await interaction.response.send_message(embed=response.error("Please enter a valid theme name"))
            return
        ret = self.build_theme_embed(name)
        await interaction.response.send_message(**ret)

    @theme.autocomplete("name")
    async def theme_autocomplete(self, interaction: discord.Interaction, query: str) -> List[app_commands.Choice[str]]:
        return [app_commands.Choice(name=name, value=name) for name in self.bot.themes.keys() if query.lower() in name.lower()][:25]


async def setup(bot: Chiffon):
    await bot.add_cog(Addon(bot))

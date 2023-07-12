import re
import discord
import traceback2
from discord import app_commands
from discord.ext import commands
from typing import List, Union
from thefuzz import process

from bot import Chiffon
import response
import settings


def parse_addon_string(meta: str) -> tuple[str, str]:
    return meta.split("@")[0], meta.split("@")[1]


class AddonDropdown(discord.ui.Select):
    """ Dropdown menu for addon embed """

    def __init__(self, addon, cands: list, user_id: int) -> None:
        """
        :param addon: Addon class
        :param cands: candidate addons
        :param user_id: the user who performed a search
        """
        self.addon: Addon = addon
        self.user_id: int = user_id
        self.cands: list = cands
        self.message: Union[None, discord.Message] = None
        # create options
        metas = [c[0] for c in cands]
        options = []
        for meta in metas:
            addon_type, addon_name = parse_addon_string(meta)
            options.append(discord.SelectOption(
                label=addon_name,
                # description="",
                emoji=settings.emojis[addon_type],
                value=meta
            ))
        super().__init__(placeholder='See other candidates', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        """
        when another addon is selected with a dropdown
        :param interaction:
        """
        if interaction.user.id != self.user_id:
            return
        # create an embed for the selected addon
        embed, view, dropdown = self.addon.build_addon_embed(self.values[0], self.cands, self.user_id)
        await interaction.response.edit_message(embed=embed, view=view)
        dropdown.set_message(self.message)
        # stop the previous view as it creates a new view
        self._view.stop()

    def set_message(self, message: discord.Message) -> None:
        """
        set the message of addon embed
        :param message: the message of addon embed
        """
        self.message = message

    async def on_timeout(self) -> None:
        self.disabled = True
        self.placeholder = "timed out"
        if self.message:
            await self.message.edit(view=self._view)


class Addon(commands.Cog):

    def __init__(self, bot: Chiffon) -> None:
        self.bot = bot
        self.message_pattern = re.compile(r".*(?<!\[)+\[\[(([\w 　]){2,})]](?!])+.*")
        # NOTE: .* -> 前後の関係ないもの / (?<!\[)+や(?!])+ -> 多すぎる[または]で囲まれたものの除去 / (([\w 　]){2,}) -> 中身は2文字以上の空白または[a-zA-Z0-9_]
        #       https://github.com/DiscordGIR/GIRRewrite/blob/6e12e10687be8e0f97c2c1adee6f6402ed44a2b6/cogs/commands/misc/canister.py#L31

    def build_plugin_embed(self, plugin_name: str) -> tuple[discord.Embed, discord.ui.View]:
        """
        build an embed for the specific plugin
        :param plugin_name: exact plugin name
        :return:
        """
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
        # add compatibility information if any
        alt = ""  # the link to fixed plugin
        if plugin_name in self.bot.compatibility["plugin"].keys():
            note = self.bot.compatibility["plugin"][plugin_name]
            if "~" in note["ver"]:  # normal
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
        view = discord.ui.View(timeout=settings.dropdown_timeout)
        view.add_item(discord.ui.Button(label="Install plugin", url=settings.plugin_install_scheme % (plugin["url"])))  # url only accepts one of ('http', 'https', 'discord')
        if alt:
            view.add_item(discord.ui.Button(label="Install fixed version [Recommended]", url=settings.plugin_install_scheme % alt))
        if "message_id" in plugin:
            view.add_item(discord.ui.Button(label="Original post", url=settings.message_link % (settings.plugins_channel, plugin["message_id"])))
        return embed, view

    def build_theme_embed(self, theme_name: str) -> tuple[discord.Embed, discord.ui.View]:
        """
        build an embed for the specific theme
        :param theme_name: exact theme name
        :return:
        """
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
        view = discord.ui.View(timeout=settings.dropdown_timeout)
        view.add_item(discord.ui.Button(label="Install theme", url=settings.theme_install_scheme % (theme["url"])))  # url only accepts one of ('http', 'https', 'discord')
        if "message_id" in theme:
            view.add_item(discord.ui.Button(label="Original post", url=settings.message_link % (settings.themes_channel, theme["message_id"])))
        return embed, view

    def build_addon_embed(self, name_with_type: str, cands: list, user_id: int) -> tuple[discord.Embed, discord.ui.View, AddonDropdown]:
        """
        build an embed for the specific addon
        :param name_with_type: addon name with addon type included (<addon_type>@<addon_name>)
        :param cands: candidates
        :param user_id: id of the user who performed this action
        :return:
        """
        # make embed for the addon
        addon_type, addon_name = parse_addon_string(name_with_type)
        embed = discord.Embed()
        view = discord.ui.View()
        if addon_type == "plugin":
            embed, view = self.build_plugin_embed(addon_name)
        elif addon_type == "theme":
            embed, view = self.build_theme_embed(addon_name)
        # create dropdown menu for other candidates
        dropdown = AddonDropdown(self, cands, user_id)
        if len(cands) > 1:
            view.add_item(dropdown)
            view.on_timeout = dropdown.on_timeout
        return embed, view, dropdown

    def generate_addon_embed(self, query: str, user_id: int, plugin: bool = False, theme: bool = False) -> Union[tuple[discord.Embed, discord.ui.View, AddonDropdown], tuple[None, None, None]]:
        """
        make an embed for addons with a query
        :param query: the query for filtering addons
        :param user_id: id of the user who performed this action
        :param plugin: whether to include plugins
        :param theme: whether to include themes
        :return: return embed, view, dropdown. if no addon was found, return None
        """
        query = query.replace("_", "").replace(" ", "").lower()  # normalize the query
        cands = []  # list of <addon_type>@<addon_name>
        # look for candidates whose name is close to the provided name
        # to mix both plugins and themes, add the special prefix to addon names and parse with parse_addon_string() later
        if plugin:
            cands += [("plugin@" + p[0], p[1]) for p in process.extract(query, self.bot.plugins.keys()) if p[1] >= 80]
        if theme:
            cands += [("theme@" + t[0], t[1]) for t in process.extract(query, self.bot.themes.keys()) if t[1] >= 80]
        if not cands:
            return None, None, None
        # sort candidates by the match ratio
        cands.sort(key=lambda x: x[1], reverse=True)
        # build an embed for the most well matched addon
        embed, view, dropdown = self.build_addon_embed(cands[0][0], cands, user_id)
        return embed, view, dropdown

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # detect changes of the database
        if message.channel.id == settings.plugin_update_channel:
            await self.bot.update_plugin_list()
        elif message.channel.id == settings.theme_update_channel:
            await self.bot.update_theme_list()

        # react to [[AddonName]]
        match = self.message_pattern.search(message.content)
        if not match:
            return
        provided_name = match.group(1)  # extract the query from match object
        embed, view, dropdown = self.generate_addon_embed(provided_name, message.author.id, True, True)
        if embed:
            message = await message.reply(embed=embed, view=view)
            dropdown.set_message(message)

    @app_commands.command(name="plugin", description="search plugins")
    async def plugin(self, interaction: discord.Interaction, query: str) -> None:
        """
        bot command that returns plugins whose name is close to the provided name
        :param interaction:
        :param query: the name provided by a user
        """
        embed, view, dropdown = self.generate_addon_embed(query, interaction.user.id, plugin=True)
        if not embed:
            await interaction.response.send_message(embed=response.error("No plugin was found. Please try changing the query."))
            return
        await interaction.response.send_message(embed=embed, view=view)
        dropdown.set_message(await interaction.original_response())

    @plugin.autocomplete("query")
    async def plugin_autocomplete(self, interaction: discord.Interaction, query: str) -> List[app_commands.Choice[str]]:
        """
        return plugins whose name includes the query text
        :param interaction:
        :param query: the query provided by a user
        :return: candidates
        """
        return [app_commands.Choice(name=name, value=name) for name in self.bot.plugins.keys() if query.lower() in name.lower()][:25]

    @app_commands.command(name="theme", description="search themes")
    async def theme(self, interaction: discord.Interaction, query: str) -> None:
        """
        bot command that returns themes whose name is close to the provided name
        :param interaction:
        :param query: the name provided by a user
        """
        embed, view, dropdown = self.generate_addon_embed(query, interaction.user.id, theme=True)
        if not embed:
            await interaction.response.send_message(embed=response.error("No theme was found. Please try changing the query."))
            return
        await interaction.response.send_message(embed=embed, view=view)
        dropdown.set_message(await interaction.original_response())

    @theme.autocomplete("query")
    async def theme_autocomplete(self, interaction: discord.Interaction, query: str) -> List[app_commands.Choice[str]]:
        """
        return themes whose name includes the query text
        :param interaction:
        :param query: the query provided by a user
        :return: candidates
        """
        return [app_commands.Choice(name=name, value=name) for name in self.bot.themes.keys() if query.lower() in name.lower()][:25]


async def setup(bot: Chiffon):
    await bot.add_cog(Addon(bot))

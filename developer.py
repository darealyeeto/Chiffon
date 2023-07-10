import discord
import traceback2
from discord import app_commands
from discord.ext import commands

from bot import Chiffon
import response
import settings


class Developer(commands.Cog):

    def __init__(self, bot: Chiffon) -> None:
        self.bot = bot

    @app_commands.command(description="Reload the specific cog")
    @app_commands.choices(name=[
        app_commands.Choice(name="addon", value="addon"),
        app_commands.Choice(name="developer", value="developer")
    ])
    async def reload(self, interaction: discord.Interaction, name: str) -> None:
        if interaction.user.id in settings.developers:
            try:
                await self.bot.reload_extension(name)
            except:
                await interaction.response.send_message(embed=response.error(f"Failed to reload '{name}'\n```py\n{traceback2.format_exc()}```"), ephemeral=True)
            else:
                await interaction.response.send_message(embed=response.success(f"Successfully reloaded '{name}'"), ephemeral=True)
        else:
            await interaction.response.send_message(embed=response.error(f"This command is only available to developers"), ephemeral=True)


async def setup(bot: Chiffon):
    await bot.add_cog(Developer(bot))

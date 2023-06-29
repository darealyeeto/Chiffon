from typing import List

import discord
import traceback2
from discord import app_commands
from discord.ext import commands

from bot import Chiffon
import response


class Developer(commands.Cog):

    def __init__(self, bot: Chiffon) -> None:
        self.bot = bot

    @app_commands.command(description="Reload the specific cog")
    async def reload(self, interaction: discord.Interaction, name: str) -> None:
        # TODO: perms check
        try:
            await self.bot.reload_extension(name)
        except:
            await interaction.response.send_message(embed=response.error(f"Failed to reload '{name}'\n```py\n{traceback2.format_exc()}```"), ephemeral=True)
        else:
            await interaction.response.send_message(embed=response.success(f"Successfully reloaded '{name}'"), ephemeral=True)


async def setup(bot: Chiffon):
    await bot.add_cog(Developer(bot))

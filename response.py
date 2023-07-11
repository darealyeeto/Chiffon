import discord
import settings


def error(text: str, title: str = None):
    embed = discord.Embed(
        description=f"{settings.emojis.xx} {text}",
        color=discord.Color.red()
    )
    if title:
        embed.title = title
    return embed


def success(text: str, title: str = None):
    embed = discord.Embed(
        description=f"{settings.emojis.oo} {text}",
        color=discord.Color.green()
    )
    if title:
        embed.title = title
    return embed


def warning(text: str, title: str = None):
    embed = discord.Embed(
        description=f"{settings.emojis.warn} {text}",
        color=0xf7b51c
    )
    if title:
        embed.title = title
    return embed


def normal(text: str, title: str = None):
    embed = discord.Embed(
        description=f"{text}",
        color=discord.Color.blue()
    )
    if title:
        embed.title = title
    return embed

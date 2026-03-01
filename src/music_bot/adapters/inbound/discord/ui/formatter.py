from __future__ import annotations

import discord


def format_success(message: str, *, title: str = "Success") -> discord.Embed:
    return discord.Embed(title=title, description=message, color=discord.Color.green())


def format_info(message: str, *, title: str = "Info") -> discord.Embed:
    return discord.Embed(title=title, description=message, color=discord.Color.blue())


def format_error(message: str, *, title: str = "Error") -> discord.Embed:
    return discord.Embed(title=title, description=message, color=discord.Color.red())

from __future__ import annotations

import discord
from discord import Interaction, app_commands
from discord.ext import commands

from music_bot.adapters.inbound.discord.cogs.base import BaseCog
from music_bot.adapters.inbound.discord.helpers import (
    disconnect_voice_client,
    ensure_voice_connected,
    require_guild,
    require_member,
)
from music_bot.adapters.inbound.discord.ui import Responder


class VoiceCog(BaseCog, name="Voice"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    @app_commands.command(name="join", description="Joins a voice channel")
    async def join(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        guild: discord.Guild = require_guild(interaction)
        member: discord.Member = require_member(interaction)

        await responder.defer()

        voice_client: discord.VoiceClient = await ensure_voice_connected(guild=guild, member=member)

        await responder.success(f"Connected to {voice_client.channel.mention}")

    @app_commands.command(name="leave", description="Leaves the current voice channel")
    async def leave(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        guild: discord.Guild = require_guild(interaction)

        await responder.defer()

        channel: discord.VoiceChannel = await disconnect_voice_client(guild=guild)

        await responder.success(f"Disconnected from {channel.mention}")

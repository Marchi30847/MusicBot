from __future__ import annotations

import discord
from discord import VoiceProtocol

from music_bot.adapters.inbound.discord.errors import (
    NotAMemberError,
    NotConnectedToVoiceError,
    NotInGuildError,
)


def require_guild(interaction: discord.Interaction) -> discord.Guild:
    guild: discord.Guild | None = interaction.guild
    if guild is None:
        raise NotInGuildError()

    return guild


def require_member(interaction: discord.Interaction) -> discord.Member:
    member: discord.Member | None = (
        interaction.user if isinstance(interaction.user, discord.Member) else None
    )
    if member is None:
        raise NotAMemberError()

    return member


def require_voice_connected(guild: discord.Guild) -> discord.VoiceClient:
    voice_protocol: VoiceProtocol | None = guild.voice_client
    if not isinstance(voice_protocol, discord.VoiceClient):
        raise NotConnectedToVoiceError()

    return voice_protocol

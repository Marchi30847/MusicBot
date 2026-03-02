from __future__ import annotations

from typing import cast

import discord
from discord import VoiceProtocol
from discord.abc import Connectable

from music_bot.adapters.inbound.discord.errors import (
    NotConnectedToVoiceError,
    NotInVoiceError,
    UnsupportedVoiceChannelError,
    VoiceConnectionError,
    VoiceForbiddenError,
    VoiceTimeoutError,
)


async def ensure_voice_connected(
    *,
    guild: discord.Guild,
    member: discord.Member,
) -> discord.VoiceClient:
    if member.voice is None or member.voice.channel is None:
        raise NotInVoiceError()

    channel: Connectable = member.voice.channel
    if not isinstance(channel, discord.VoiceChannel):
        raise UnsupportedVoiceChannelError()

    voice_protocol: VoiceProtocol | None = guild.voice_client

    if voice_protocol is not None and voice_protocol.channel == channel:
        return cast(discord.VoiceClient, voice_protocol)

    try:
        if voice_protocol is not None:
            voice_client: discord.VoiceClient = cast(discord.VoiceClient, voice_protocol)
            await voice_client.move_to(channel)
            return voice_client

        new_voice_client: discord.VoiceClient = await channel.connect()
        return new_voice_client

    except TimeoutError as exc:
        raise VoiceTimeoutError() from exc
    except discord.Forbidden as exc:
        raise VoiceForbiddenError() from exc
    except (discord.ClientException, discord.HTTPException) as exc:
        raise VoiceConnectionError() from exc


async def disconnect_voice_client(
    *,
    guild: discord.Guild,
) -> discord.VoiceChannel:
    voice_protocol: VoiceProtocol | None = guild.voice_client
    if voice_protocol is None:
        raise NotConnectedToVoiceError()

    channel: Connectable = voice_protocol.channel

    try:
        await voice_protocol.disconnect(force=False)
    except TimeoutError as exc:
        raise VoiceTimeoutError() from exc
    except (discord.ClientException, discord.HTTPException) as exc:
        raise VoiceConnectionError() from exc

    return cast(discord.VoiceChannel, channel)

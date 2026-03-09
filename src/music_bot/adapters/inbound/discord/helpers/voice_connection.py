from __future__ import annotations

import discord

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
    voice_state: discord.VoiceState | None = member.voice
    if voice_state is None or voice_state.channel is None:
        raise NotInVoiceError()

    channel_any: discord.abc.Connectable = voice_state.channel
    if not isinstance(channel_any, discord.VoiceChannel):
        raise UnsupportedVoiceChannelError()

    channel: discord.VoiceChannel = channel_any

    vc_any: discord.VoiceProtocol | None = guild.voice_client
    if isinstance(vc_any, discord.VoiceClient) and vc_any.channel == channel:
        existing_vc: discord.VoiceClient = vc_any
        return existing_vc

    try:
        if isinstance(vc_any, discord.VoiceClient):
            existing_vc2: discord.VoiceClient = vc_any
            await existing_vc2.move_to(channel)
            return existing_vc2

        new_vc: discord.VoiceClient = await channel.connect()
        return new_vc

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
    vc_any: discord.VoiceProtocol | None = guild.voice_client
    if not isinstance(vc_any, discord.VoiceClient):
        raise NotConnectedToVoiceError()

    vc: discord.VoiceClient = vc_any

    channel_any: discord.abc.Connectable = vc.channel
    if not isinstance(channel_any, discord.VoiceChannel):
        raise UnsupportedVoiceChannelError()

    channel: discord.VoiceChannel = channel_any

    try:
        await vc.disconnect(force=False)
    except TimeoutError as exc:
        raise VoiceTimeoutError() from exc
    except (discord.ClientException, discord.HTTPException) as exc:
        raise VoiceConnectionError() from exc

    return channel

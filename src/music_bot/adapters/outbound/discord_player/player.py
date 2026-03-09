from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL


class DiscordPlayer:
    def __init__(self, bot: commands.Bot | None = None) -> None:
        self._bot: commands.Bot | None = bot

    async def play(
        self, *, context_id: int, url: str, on_finished: Callable[[int, Exception | None], None]
    ) -> None:
        vc: discord.VoiceClient = self._get_vc(context_id)

        if vc.is_playing():
            raise RuntimeError(f"Already playing in guild {context_id}")

        raw_url: str = await asyncio.to_thread(self._yt_dlp_resolver, url)
        before_options: str = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        options: str = "-vn"

        audio_source: discord.FFmpegPCMAudio = discord.FFmpegPCMAudio(
            source=raw_url,
            before_options=before_options,
            options=options,
        )

        vc.play(audio_source, after=lambda exc: on_finished(context_id, exc))

    async def stop(self, *, context_id: int) -> None:
        vc: discord.VoiceClient = self._get_vc(context_id)

        vc.stop()

    async def pause(self, *, context_id: int) -> None:
        vc: discord.VoiceClient = self._get_vc(context_id)

        if vc.is_playing():
            vc.pause()

    async def resume(self, *, context_id: int) -> None:
        vc: discord.VoiceClient = self._get_vc(context_id)

        if vc.is_paused():
            vc.resume()

    async def is_playing(self, *, context_id: int) -> bool:
        vc: discord.VoiceClient = self._get_vc(context_id)

        return vc.is_playing()

    async def is_paused(self, *, context_id: int) -> bool:
        vc: discord.VoiceClient = self._get_vc(context_id)

        return vc.is_paused()

    def _get_vc(self, context_id: int) -> discord.VoiceClient:
        if self._bot is None:
            raise RuntimeError("Bot not attached")

        guild: discord.Guild | None = self._bot.get_guild(context_id)
        if guild is None:
            raise RuntimeError(f"Guild {context_id} not found")

        vc: discord.VoiceProtocol | None = guild.voice_client
        if not isinstance(vc, discord.VoiceClient):
            raise RuntimeError(f"Not connected to voice in guild {context_id}")

        return vc

    def _yt_dlp_resolver(self, url: str) -> str:
        yt_dlp_params: dict[str, Any] = {
            "format": "bestaudio/best",
            "noplaylist": True,
        }
        with YoutubeDL(yt_dlp_params) as ydl:  # type: ignore[arg-type]
            info: dict[str, Any] = ydl.extract_info(url, download=False)  # type: ignore[assignment]

        if "entries" in info and isinstance(info["entries"], list) and info["entries"]:
            first: Any = info["entries"][0]
            if isinstance(first, dict):
                info = first

        stream_url: Any = info.get("url")

        if not isinstance(stream_url, str) or not stream_url:
            raise RuntimeError("yt-dlp could not resolve a playable audio URL")

        return stream_url

    def attach_bot(self, bot: commands.Bot) -> None:
        self._bot = bot

from __future__ import annotations

from music_bot.adapters.inbound.discord.bot import MusicBot
from music_bot.bootstrap.settings import Settings

from .build import build_discord_bot


async def run_discord_bot(settings: Settings) -> None:
    token: str = settings.discord_token.get_secret_value()

    bot: MusicBot = build_discord_bot(settings)

    await bot.start(token)

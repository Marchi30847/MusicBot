from __future__ import annotations

from discord import Intents

from music_bot.adapters.inbound.discord.bot import MusicBot
from music_bot.bootstrap.settings import Settings


def build_discord_bot(settings: Settings) -> MusicBot:
    intents: Intents = Intents.default()

    bot: MusicBot = MusicBot(
        intents=intents, dependencies=None, dev_guild_id=settings.discord_guild_id
    )

    return bot

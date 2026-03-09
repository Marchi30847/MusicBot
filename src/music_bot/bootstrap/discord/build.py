from __future__ import annotations

from discord import Intents

from music_bot.adapters.inbound.discord.bot import MusicBot
from music_bot.adapters.outbound.discord_player import DiscordPlayer
from music_bot.application.ports import MusicPlayer
from music_bot.bootstrap.di import build_discord_dependencies
from music_bot.bootstrap.settings import Settings


def build_discord_bot(settings: Settings) -> MusicBot:
    intents: Intents = Intents.default()

    discord_player: DiscordPlayer = DiscordPlayer()
    music_player: MusicPlayer = discord_player

    bot: MusicBot = MusicBot(
        intents=intents,
        dependencies=build_discord_dependencies(music_player),
        dev_guild_id=settings.discord_guild_id,
    )
    discord_player.attach_bot(bot)

    return bot

from __future__ import annotations

from music_bot.adapters.inbound.discord.bot.dependencies import DiscordDependencies
from music_bot.adapters.inbound.discord.cogs import PlaybackDependencies


def to_playback_dependencies(root: DiscordDependencies) -> PlaybackDependencies:
    return PlaybackDependencies(
        enqueue=root.enqueue,
        dequeue=root.dequeue,
    )

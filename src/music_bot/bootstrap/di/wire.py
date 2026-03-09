from __future__ import annotations

from music_bot.adapters.inbound.discord.bot.dependencies import DiscordDependencies
from music_bot.adapters.outbound.in_memory.music import InMemoryQueueRepository
from music_bot.application.orchestration.music import MusicActorManager
from music_bot.application.ports import MusicPlayer
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.application.use_cases.music import (
    NowPlayingUseCase,
    PlayUrlUseCase,
    SkipUseCase,
    StopUseCase,
)


def build_discord_dependencies(music_player: MusicPlayer) -> DiscordDependencies:
    queue_repository: QueueRepository = InMemoryQueueRepository()

    music_actor_manager = MusicActorManager(
        queue_repository=queue_repository, music_player=music_player
    )

    dependencies: DiscordDependencies = DiscordDependencies(
        play_url=PlayUrlUseCase(music_actor_manager),
        stop=StopUseCase(music_actor_manager),
        skip=SkipUseCase(music_actor_manager),
        now_playing=NowPlayingUseCase(music_actor_manager),
    )

    return dependencies

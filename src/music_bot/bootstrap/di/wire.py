from __future__ import annotations

from music_bot.adapters.inbound.discord.bot.dependencies import DiscordDependencies
from music_bot.adapters.outbound.in_memory.music import InMemoryQueueRepository
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.application.use_cases.music import DequeueUseCase, EnqueueUseCase


def build_discord_dependencies() -> DiscordDependencies:
    queue_repository: QueueRepository = InMemoryQueueRepository()

    return DiscordDependencies(
        enqueue=EnqueueUseCase(queue_repository=queue_repository),
        dequeue=DequeueUseCase(queue_repository=queue_repository),
    )

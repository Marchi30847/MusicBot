from __future__ import annotations

from music_bot.application.contracts.commands.music import EnqueueCommand
from music_bot.application.contracts.results.music import EnqueueResult
from music_bot.application.mappers.music import map_enqueue_command_to_track
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.domain.music.models import Queue, Track


class EnqueueUseCase:
    def __init__(self, queue_repository: QueueRepository) -> None:
        self._repository: QueueRepository = queue_repository

    def execute(self, command: EnqueueCommand) -> EnqueueResult:
        track: Track = map_enqueue_command_to_track(command)
        guild_id: int = command.guild_id

        queue: Queue = self._repository.get_or_create(guild_id)
        queue.enqueue(track)
        self._repository.save(guild_id, queue)

        return EnqueueResult(queue_size=len(queue))

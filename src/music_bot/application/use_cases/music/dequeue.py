from __future__ import annotations

from music_bot.application.contracts.commands.music.dequeue import DequeueCommand
from music_bot.application.contracts.results.music.dequeue import DequeueResult
from music_bot.application.mappers.music.track import map_track_to_dto
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.domain.music.models import Queue, Track


class DequeueUseCase:
    def __init__(self, queue_repository: QueueRepository) -> None:
        self._repository: QueueRepository = queue_repository

    def execute(self, command: DequeueCommand) -> DequeueResult:
        guild_id: int = command.guild_id

        queue: Queue | None = self._repository.get(guild_id)
        if queue is None:
            return DequeueResult(queue_size=0, track=None)

        track: Track | None = queue.dequeue()
        if track is None:
            return DequeueResult(queue_size=len(queue), track=None)

        self._repository.save(guild_id, queue)

        return DequeueResult(queue_size=len(queue), track=map_track_to_dto(track))

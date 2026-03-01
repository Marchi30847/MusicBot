from __future__ import annotations

from music_bot.domain.music.models import Queue


class InMemoryQueueRepository:
    def __init__(self) -> None:
        self._queues: dict[int, Queue] = {}

    def get(self, guild_id: int) -> Queue | None:
        return self._queues.get(guild_id)

    def get_or_create(self, guild_id: int) -> Queue:
        queue: Queue | None = self._queues.get(guild_id)
        if queue is None:
            self._queues[guild_id] = queue = Queue()

        return queue

    def save(self, guild_id: int, queue: Queue) -> None:
        self._queues[guild_id] = queue

    def delete(self, guild_id: int) -> None:
        self._queues.pop(guild_id, None)

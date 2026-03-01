from __future__ import annotations

from typing import Protocol

from music_bot.domain.music.models import Queue


class QueueRepository(Protocol):
    def get(self, guild_id: int) -> Queue | None: ...

    def get_or_create(self, guild_id: int) -> Queue: ...

    def save(self, guild_id: int, queue: Queue) -> None: ...

    def delete(self, guild_id: int) -> None: ...

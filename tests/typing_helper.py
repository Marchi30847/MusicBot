from typing import Protocol

from music_bot.application.contracts.commands.music import DequeueCommand, EnqueueCommand
from music_bot.domain.music.models import Track


class MakeTrack(Protocol):
    def __call__(self, url: str, requested_by: int = 1) -> Track: ...


class MakeEnqueueCommand(Protocol):
    def __call__(
        self,
        guild_id: int,
        url: str,
        requested_by: int,
        title: str | None = None,
    ) -> EnqueueCommand: ...


class MakeDequeueCommand(Protocol):
    def __call__(self, guild_id: int, requested_by: int) -> DequeueCommand: ...

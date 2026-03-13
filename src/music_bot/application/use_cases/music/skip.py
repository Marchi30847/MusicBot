from __future__ import annotations

from music_bot.application.contracts.commands.music import SkipCommand
from music_bot.application.contracts.results.music import SkipResult
from music_bot.application.orchestration.music import MusicActorManager


class SkipUseCase:
    def __init__(self, manager: MusicActorManager) -> None:
        self._manager: MusicActorManager = manager

    async def __call__(self, command: SkipCommand) -> SkipResult:
        return await self._manager.get_or_create(command.guild_id).send_skip(command)

from __future__ import annotations

from music_bot.application.contracts.commands.music import StopCommand
from music_bot.application.contracts.results.music import StopResult
from music_bot.application.orchestration.music import MusicActorManager


class StopUseCase:
    def __init__(self, manager: MusicActorManager) -> None:
        self._manager: MusicActorManager = manager

    async def execute(self, command: StopCommand) -> StopResult:
        return await self._manager.get_or_create(command.guild_id).send_stop(command)

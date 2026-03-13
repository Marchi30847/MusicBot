from __future__ import annotations

from music_bot.application.contracts.commands.music import PlayUrlCommand
from music_bot.application.contracts.results.music import PlayUrlResult
from music_bot.application.orchestration.music import MusicActorManager


class PlayUrlUseCase:
    def __init__(self, manager: MusicActorManager) -> None:
        self._manager: MusicActorManager = manager

    async def __call__(self, command: PlayUrlCommand) -> PlayUrlResult:
        return await self._manager.get_or_create(command.guild_id).send_play_url(command)

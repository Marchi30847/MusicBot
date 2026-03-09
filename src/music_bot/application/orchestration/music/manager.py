from __future__ import annotations

import asyncio

from music_bot.application.ports import MusicPlayer, QueueRepository

from .guild_actor import GuildActor


class MusicActorManager:
    def __init__(
        self,
        *,
        queue_repository: QueueRepository,
        music_player: MusicPlayer,
    ) -> None:
        self._actors: dict[int, GuildActor] = {}

        self._queue_repository: QueueRepository = queue_repository
        self._music_player: MusicPlayer = music_player

    def get_or_create(self, guild_id: int) -> GuildActor:
        if guild_id not in self._actors:
            actor: GuildActor = GuildActor(
                queue_repository=self._queue_repository,
                music_player=self._music_player,
            )
            actor.start()
            self._actors[guild_id] = actor

        return self._actors[guild_id]

    def get(self, guild_id: int) -> GuildActor | None:
        return self._actors.get(guild_id)

    async def stop(self, guild_id: int) -> None:
        actor: GuildActor | None = self._actors.get(guild_id)
        if actor is not None:
            await actor.stop()

    async def stop_and_remove(self, guild_id: int) -> None:
        await self.stop(guild_id)

        self._actors.pop(guild_id, None)

    async def shutdown(self) -> None:
        await asyncio.gather(*(actor.stop() for actor in self._actors.values()))
        self._actors.clear()

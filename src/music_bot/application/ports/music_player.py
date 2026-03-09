from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class MusicPlayer(Protocol):
    async def play(
        self, *, context_id: int, url: str, on_finished: Callable[[int, Exception | None], None]
    ) -> None: ...

    async def stop(self, *, context_id: int) -> None: ...

    async def pause(self, *, context_id: int) -> None: ...

    async def resume(self, *, context_id: int) -> None: ...

    async def is_playing(self, *, context_id: int) -> bool: ...

    async def is_paused(self, *, context_id: int) -> bool: ...

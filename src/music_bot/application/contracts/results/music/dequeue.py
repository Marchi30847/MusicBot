from __future__ import annotations

from dataclasses import dataclass

from .track import TrackDto


@dataclass(frozen=True, slots=True)
class DequeueResult:
    queue_size: int
    track: TrackDto | None

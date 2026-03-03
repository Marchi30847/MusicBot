from __future__ import annotations

from dataclasses import dataclass

from music_bot.application.use_cases.music import DequeueUseCase, EnqueueUseCase


@dataclass(frozen=True, slots=True, kw_only=True)
class PlaybackDependencies:
    enqueue: EnqueueUseCase
    dequeue: DequeueUseCase

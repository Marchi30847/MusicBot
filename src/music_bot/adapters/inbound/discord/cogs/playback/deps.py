from __future__ import annotations

from dataclasses import dataclass

from music_bot.application.use_cases.music import (
    NowPlayingUseCase,
    PlayUrlUseCase,
    SkipUseCase,
    StopUseCase,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PlaybackDependencies:
    play_url: PlayUrlUseCase
    stop: StopUseCase
    skip: SkipUseCase
    now_playing: NowPlayingUseCase

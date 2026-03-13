from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Final

from music_bot.domain.music.models import Track


class PlaybackState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"


class _Unset:
    __slots__ = ()


_UNSET: Final[_Unset] = _Unset()


@dataclass(frozen=True, slots=True, kw_only=True)
class StateContainer:
    playback_state: PlaybackState = PlaybackState.IDLE
    current_track: Track | None = None

    def copy_with(
        self,
        *,
        playback_state: PlaybackState | _Unset = _UNSET,
        current_track: Track | _Unset | None = _UNSET,
    ) -> StateContainer:
        new_playback_state: PlaybackState = self.playback_state
        if not isinstance(playback_state, _Unset):
            new_playback_state = playback_state

        new_current_track: Track | None = self.current_track
        if not isinstance(current_track, _Unset):
            new_current_track = current_track

        return replace(
            self,
            playback_state=new_playback_state,
            current_track=new_current_track,
        )

    @property
    def is_idle(self) -> bool:
        return self.playback_state is PlaybackState.IDLE

    @property
    def is_playing(self) -> bool:
        return self.playback_state is PlaybackState.PLAYING

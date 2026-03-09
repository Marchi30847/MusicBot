from __future__ import annotations

from asyncio import Future
from dataclasses import dataclass

from music_bot.application.contracts.commands.music import (
    NowPlayingCommand,
    PlayUrlCommand,
    SkipCommand,
    StopCommand,
)
from music_bot.application.contracts.results.music import (
    NowPlayingResult,
    PlayUrlResult,
    SkipResult,
    StopResult,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Request[TCommand, TResult]:
    command: TCommand
    future: Future[TResult]


@dataclass(frozen=True, slots=True, kw_only=True)
class PlayUrlRequest(Request[PlayUrlCommand, PlayUrlResult]):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class StopRequest(Request[StopCommand, StopResult]):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class SkipRequest(Request[SkipCommand, SkipResult]):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class NowPlayingRequest(Request[NowPlayingCommand, NowPlayingResult]):
    pass


@dataclass(frozen=True, slots=True, kw_only=True)
class TryStartEvent:
    guild_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class TrackFinishedEvent:
    guild_id: int
    exception: Exception | None

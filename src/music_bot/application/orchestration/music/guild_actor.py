from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

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
from music_bot.application.ports import MusicPlayer, QueueRepository

from .events import (
    NowPlayingRequest,
    PlayUrlRequest,
    Request,
    SkipRequest,
    StopRequest,
    TrackFinishedEvent,
    TryStartEvent,
)
from .playback_service import PlaybackService

type EventMessage = TryStartEvent | TrackFinishedEvent
type Message = Request[Any, Any] | EventMessage

logger: logging.Logger = logging.getLogger(__name__)


class GuildActor:
    def __init__(
        self,
        *,
        queue_repository: QueueRepository,
        music_player: MusicPlayer,
        playback_service: PlaybackService | None = None,
    ) -> None:
        self._playback_service: PlaybackService = playback_service or PlaybackService(
            queue_repository=queue_repository,
            music_player=music_player,
        )

        self._mailbox: asyncio.Queue[Message] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is not None:
            raise RuntimeError("GuildActor is already running")

        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None
            self._reject_pending_messages(RuntimeError("GuildActor stopped"))

    def _reject_pending_messages(self, stop_exception: Exception) -> None:
        while True:
            try:
                msg: Message = self._mailbox.get_nowait()
            except asyncio.QueueEmpty:
                break

            if isinstance(msg, Request) and not msg.future.done():
                msg.future.set_exception(stop_exception)

            self._mailbox.task_done()

    async def send_play_url(self, command: PlayUrlCommand) -> PlayUrlResult:
        return await self._send_request(PlayUrlRequest, command)

    async def send_stop(self, command: StopCommand) -> StopResult:
        return await self._send_request(StopRequest, command)

    async def send_skip(self, command: SkipCommand) -> SkipResult:
        return await self._send_request(SkipRequest, command)

    async def send_now_playing(self, command: NowPlayingCommand) -> NowPlayingResult:
        return await self._send_request(NowPlayingRequest, command)

    def _emit_track_finished(self, event: TrackFinishedEvent) -> None:
        if self._task is None:
            return

        self._mailbox.put_nowait(event)

    async def _send_request[TCommand, TResult](
        self,
        request_cls: type[Request[TCommand, TResult]],
        command: TCommand,
    ) -> TResult:
        self._ensure_running()

        ftr: asyncio.Future[TResult] = asyncio.get_running_loop().create_future()
        req: Request[TCommand, TResult] = request_cls(command=command, future=ftr)

        await self._mailbox.put(req)
        return await ftr

    def _ensure_running(self) -> None:
        if self._task is None:
            raise RuntimeError("GuildActor is not running. Call start() first.")

    async def _run(self) -> None:
        while True:
            msg: Message = await self._mailbox.get()
            try:
                match msg:
                    case PlayUrlRequest(command=cmd, future=ftr):
                        play_url_result, events = await self._playback_service.handle_play_url(cmd)
                        await self._enqueue_events(events)
                        self._resolve_future(ftr, play_url_result)

                    case StopRequest(command=cmd, future=ftr):
                        stop_result, events = await self._playback_service.handle_stop(cmd)
                        await self._enqueue_events(events)
                        self._resolve_future(ftr, stop_result)

                    case SkipRequest(command=cmd, future=ftr):
                        skip_result, events = await self._playback_service.handle_skip(cmd)
                        await self._enqueue_events(events)
                        self._resolve_future(ftr, skip_result)

                    case NowPlayingRequest(command=cmd, future=ftr):
                        (
                            now_playing_result,
                            events,
                        ) = await self._playback_service.handle_now_playing(cmd)
                        await self._enqueue_events(events)
                        self._resolve_future(ftr, now_playing_result)

                    case TryStartEvent(guild_id=gid):
                        await self._playback_service.handle_try_start(
                            guild_id=gid,
                            emit_finished_event=self._emit_track_finished,
                        )

                    case TrackFinishedEvent() as event:
                        events = await self._playback_service.handle_track_finished(event)
                        await self._enqueue_events(events)

                    case _:
                        logger.warning(f"Unexpected message: {msg}")

            except Exception as exc:
                if isinstance(msg, Request) and not msg.future.done():
                    msg.future.set_exception(exc)
                else:
                    logger.exception(
                        f"Unhandled exception in GuildActor while processing {msg}", exc_info=True
                    )

            finally:
                self._mailbox.task_done()

    async def _enqueue_events(self, events: Sequence[EventMessage]) -> None:
        for event in events:
            await self._mailbox.put(event)

    def _resolve_future[TResult](self, future: asyncio.Future[TResult], value: TResult) -> None:
        if not future.done():
            future.set_result(value)

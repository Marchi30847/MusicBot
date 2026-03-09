from __future__ import annotations

import asyncio
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
from music_bot.application.mappers.music import map_play_url_command_to_track, map_track_to_dto
from music_bot.application.ports import MusicPlayer, QueueRepository
from music_bot.domain.music.models import Queue, Track

from .events import (
    NowPlayingRequest,
    PlayUrlRequest,
    Request,
    SkipRequest,
    StopRequest,
    TrackFinishedEvent,
    TryStartEvent,
)
from .states import PlaybackState

type EventMessage = TryStartEvent | TrackFinishedEvent
type Message = Request[Any, Any] | EventMessage


class GuildActor:
    def __init__(
        self,
        *,
        queue_repository: QueueRepository,
        music_player: MusicPlayer,
    ) -> None:
        self._queue_repository: QueueRepository = queue_repository
        self._music_player: MusicPlayer = music_player

        self._mailbox: asyncio.Queue[Message] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None

        self._state: PlaybackState = PlaybackState.IDLE
        self._current_track: Track | None = None

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

        stop_exc: RuntimeError = RuntimeError("GuildActor stopped")
        while True:
            try:
                msg: Message = self._mailbox.get_nowait()
            except asyncio.QueueEmpty:
                break

            if isinstance(msg, (PlayUrlRequest, StopRequest, SkipRequest, NowPlayingRequest)):
                if not msg.future.done():
                    msg.future.set_exception(stop_exc)

            self._mailbox.task_done()

    async def _send_request[TCommand, TResult](
        self,
        request_cls: type[Request[TCommand, TResult]],
        command: TCommand,
    ) -> TResult:
        self._ensure_running()

        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        ftr: asyncio.Future[TResult] = loop.create_future()

        req: Request[TCommand, TResult] = request_cls(command=command, future=ftr)
        await self._mailbox.put(req)

        return await ftr

    async def send_play_url(self, command: PlayUrlCommand) -> PlayUrlResult:
        return await self._send_request(PlayUrlRequest, command)

    async def send_stop(self, command: StopCommand) -> StopResult:
        return await self._send_request(StopRequest, command)

    async def send_skip(self, command: SkipCommand) -> SkipResult:
        return await self._send_request(SkipRequest, command)

    async def send_now_playing(self, command: NowPlayingCommand) -> NowPlayingResult:
        return await self._send_request(NowPlayingRequest, command)

    def _send_try_start(self, guild_id: int) -> None:
        self._ensure_running()

        self._mailbox.put_nowait(TryStartEvent(guild_id=guild_id))

    def _send_track_finished(self, event: TrackFinishedEvent) -> None:
        self._ensure_running()

        self._mailbox.put_nowait(event)

    def _ensure_running(self) -> None:
        if self._task is None:
            raise RuntimeError("GuildActor is not running. Call start() first.")

    async def _run(self) -> None:
        while True:
            msg: Message = await self._mailbox.get()
            try:
                match msg:
                    case PlayUrlRequest(command=cmd, future=ftr):
                        await self._complete(ftr, self._handle_play_url(cmd))
                    case StopRequest(command=cmd, future=ftr):
                        await self._complete(ftr, self._handle_stop(cmd))
                    case SkipRequest(command=cmd, future=ftr):
                        await self._complete(ftr, self._handle_skip(cmd))
                    case NowPlayingRequest(command=cmd, future=ftr):
                        await self._complete(ftr, self._handle_now_playing(cmd))
                    case TryStartEvent(guild_id=gid):
                        await self._handle_try_start(guild_id=gid)
                    case TrackFinishedEvent() as event:
                        await self._handle_track_finished(event)
            except Exception as exc:
                self._reject(msg, exc)
            finally:
                self._mailbox.task_done()

    async def _complete(self, future: asyncio.Future[Any], coro: Any) -> None:
        if not future.done():
            future.set_result(await coro)

    def _reject(self, msg: Message, exc: Exception) -> None:
        ftr: Any = getattr(msg, "future", None)
        if ftr and isinstance(ftr, asyncio.Future) and not ftr.done():
            ftr.set_exception(exc)

    async def _handle_track_finished(self, event: TrackFinishedEvent) -> None:
        self._state = PlaybackState.IDLE
        self._current_track = None

        self._send_try_start(event.guild_id)

    async def _handle_play_url(self, command: PlayUrlCommand) -> PlayUrlResult:
        track: Track = map_play_url_command_to_track(command)
        guild_id: int = command.guild_id

        track_queue: Queue = self._queue_repository.get_or_create(guild_id)
        track_queue.enqueue(track)
        self._queue_repository.save(guild_id, track_queue)

        self._send_try_start(guild_id)

        return PlayUrlResult(queue_size=len(track_queue), enqueued=True)

    async def _handle_stop(self, command: StopCommand) -> StopResult:
        guild_id: int = command.guild_id

        queue: Queue | None = self._queue_repository.get(guild_id)
        cleared: int = len(queue) if queue is not None else 0

        self._queue_repository.delete(guild_id)

        await self._music_player.stop(context_id=guild_id)
        self._state = PlaybackState.IDLE

        self._current_track = None

        return StopResult(stopped=True, cleared=cleared)

    async def _handle_skip(self, command: SkipCommand) -> SkipResult:
        guild_id: int = command.guild_id

        had_something: bool = self._state is not PlaybackState.IDLE
        if self._state is not PlaybackState.IDLE:
            self._state = PlaybackState.IDLE
            await self._music_player.stop(context_id=guild_id)
            self._current_track = None

        self._send_try_start(guild_id)

        return SkipResult(
            skipped=had_something,
            now_playing=map_track_to_dto(self._current_track) if self._current_track else None,
        )

    async def _handle_now_playing(self, command: NowPlayingCommand) -> NowPlayingResult:
        return NowPlayingResult(
            is_playing=self._state is PlaybackState.PLAYING,
            track=map_track_to_dto(self._current_track) if self._current_track else None,
        )

    async def _handle_try_start(self, *, guild_id: int) -> bool:
        if self._state is PlaybackState.PLAYING:
            return False

        queue: Queue | None = self._queue_repository.get(guild_id)
        if queue is None:
            return False

        track: Track | None = queue.dequeue()
        if track is None:
            return False

        self._queue_repository.save(guild_id, queue)

        self._current_track = track

        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        def _after_playing(context_id: int, exception: Exception | None) -> None:
            loop.call_soon_threadsafe(
                self._send_track_finished,
                TrackFinishedEvent(guild_id=context_id, exception=exception),
            )

        await self._music_player.play(
            context_id=guild_id,
            url=track.url,
            on_finished=_after_playing,
        )

        self._state = PlaybackState.PLAYING

        return True

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any
from unittest import mock

import pytest
from tests.typing_helper import (
    MakeNowPlayingCommand,
    MakePlayUrlCommand,
    MakeSkipCommand,
    MakeStopCommand,
    MakeTrack,
)

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
from music_bot.application.orchestration.music.events import TrackFinishedEvent, TryStartEvent
from music_bot.application.orchestration.music.playback_service import PlaybackService
from music_bot.application.orchestration.music.states import PlaybackState
from music_bot.application.ports import MusicPlayer, QueueRepository
from music_bot.domain.music.models import Queue, Track


@pytest.fixture
def queue_repository() -> mock.Mock:
    repo: mock.Mock = mock.Mock(spec=QueueRepository)

    q: Queue = Queue()

    repo.get_or_create = mock.Mock(return_value=q)
    repo.get = mock.Mock(return_value=q)
    repo.save = mock.Mock(return_value=None)
    repo.delete = mock.Mock(return_value=None)

    return repo


@pytest.fixture
def music_player() -> mock.Mock:
    player: mock.Mock = mock.Mock(spec=MusicPlayer)

    player.play = mock.AsyncMock(return_value=None)
    player.stop = mock.AsyncMock(return_value=None)
    player.pause = mock.AsyncMock(return_value=None)
    player.is_playing = mock.AsyncMock(return_value=False)
    player.is_paused = mock.AsyncMock(return_value=False)
    return player


@pytest.fixture
def playback_service(
    queue_repository: QueueRepository, music_player: MusicPlayer
) -> PlaybackService:
    return PlaybackService(
        queue_repository=queue_repository,
        music_player=music_player,
    )


@pytest.mark.unit
@pytest.mark.asyncio
class TestPlaybackService:
    async def test_handle_play_url_enqueues_track_and_returns_queue_size_and_try_start_event(
        self,
        queue_repository: mock.Mock,
        playback_service: PlaybackService,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        guild_id: int = 1

        q: Queue = queue_repository.get_or_create.return_value

        command: PlayUrlCommand = make_play_url_command(guild_id=guild_id)

        container: tuple[
            PlayUrlResult, Sequence[TryStartEvent]
        ] = await playback_service.handle_play_url(command)
        result: PlayUrlResult = container[0]
        events: Sequence[TryStartEvent] = container[1]

        assert result.enqueued is True
        assert result.queue_size == 1
        assert list(events) == [TryStartEvent(guild_id=guild_id)]

        queue_repository.get_or_create.assert_called_once_with(guild_id)
        queue_repository.save.assert_called_once_with(guild_id, q)

    async def test_handle_play_url_does_not_touch_player_directly(
        self,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        command: PlayUrlCommand = make_play_url_command()

        await playback_service.handle_play_url(command)

        music_player.play.assert_not_awaited()
        music_player.stop.assert_not_awaited()
        music_player.pause.assert_not_awaited()
        music_player.is_playing.assert_not_awaited()
        music_player.is_paused.assert_not_awaited()

    async def test_handle_stop_clears_queue_calls_player_stop_and_transitions_to_idle(
        self,
        queue_repository: mock.Mock,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_stop_command: MakeStopCommand,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        q: Queue = Queue()
        q.enqueue(make_track())
        queue_repository.get.return_value = q

        command: StopCommand = make_stop_command(guild_id=guild_id)

        container: tuple[StopResult, Sequence[TryStartEvent]] = await playback_service.handle_stop(
            command
        )
        result: StopResult = container[0]
        events: Sequence[TryStartEvent] = container[1]

        assert result == StopResult(stopped=True, cleared=1)
        assert list(events) == []
        assert playback_service.state.current_track is None
        assert playback_service.state.is_idle is True

        queue_repository.get.assert_called_once_with(guild_id)
        queue_repository.delete.assert_called_once_with(guild_id)
        music_player.stop.assert_awaited_once_with(context_id=guild_id)

    async def test_handle_stop_returns_cleared_count_when_queue_missing(
        self,
        queue_repository: mock.Mock,
        playback_service: PlaybackService,
        make_stop_command: MakeStopCommand,
    ) -> None:
        guid_id: int = 1

        queue_repository.get.return_value = None

        command: StopCommand = make_stop_command(guild_id=guid_id)

        container: tuple[StopResult, Sequence[TryStartEvent]] = await playback_service.handle_stop(
            command
        )
        result: StopResult = container[0]
        events: Sequence[TryStartEvent] = container[1]

        assert result == StopResult(stopped=True, cleared=0)
        assert list(events) == []

        queue_repository.get.assert_called_once_with(guid_id)
        queue_repository.delete.assert_called_once_with(guid_id)

    async def test_handle_skip_when_idle_does_not_call_player_stop_and_emits_no_events(
        self,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_skip_command: MakeSkipCommand,
    ) -> None:
        command: SkipCommand = make_skip_command()

        container: tuple[SkipResult, Sequence[TryStartEvent]] = await playback_service.handle_skip(
            command
        )
        result: SkipResult = container[0]
        events: Sequence[TryStartEvent] = container[1]

        assert result == SkipResult(skipped=False, now_playing=None)
        assert list(events) == []
        assert playback_service.state.is_idle is True

        music_player.stop.assert_not_awaited()

    async def test_handle_skip_when_playing_calls_player_stop_transitions_to_idle_and_emits_try_start(
        self,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_skip_command: MakeSkipCommand,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        playback_service._transition_to(playback_state=PlaybackState.PLAYING, track=make_track())

        command: SkipCommand = make_skip_command(guild_id=guild_id)

        container: tuple[SkipResult, Sequence[TryStartEvent]] = await playback_service.handle_skip(
            command
        )
        result: SkipResult = container[0]
        events: Sequence[TryStartEvent] = container[1]

        assert result == SkipResult(skipped=True, now_playing=None)
        assert list(events) == [TryStartEvent(guild_id=guild_id)]
        assert playback_service.state.is_idle is True

        music_player.stop.assert_awaited_once_with(context_id=guild_id)
        music_player.play.assert_not_awaited()

    async def test_handle_now_playing_returns_track_none_when_idle(
        self,
        playback_service: PlaybackService,
        make_now_playing_command: MakeNowPlayingCommand,
    ) -> None:
        command: NowPlayingCommand = make_now_playing_command()

        container: tuple[
            NowPlayingResult, Sequence[Any]
        ] = await playback_service.handle_now_playing(command)
        result: NowPlayingResult = container[0]
        events: Sequence[Any] = container[1]

        assert result.is_playing is False
        assert result.track is None
        assert list(events) == []
        assert playback_service.state.is_idle is True

    async def test_handle_now_playing_returns_track_when_playing(
        self,
        playback_service: PlaybackService,
        make_now_playing_command: MakeNowPlayingCommand,
        make_track: MakeTrack,
    ) -> None:
        track: Track = make_track()

        playback_service._transition_to(playback_state=PlaybackState.PLAYING, track=track)

        command: NowPlayingCommand = make_now_playing_command()

        container: tuple[
            NowPlayingResult, Sequence[Any]
        ] = await playback_service.handle_now_playing(command)
        result: NowPlayingResult = container[0]
        events: Sequence[Any] = container[1]

        assert result.is_playing is True
        assert result.track is not None
        assert result.track.url == track.url
        assert list(events) == []
        assert playback_service.state.is_playing is True

    async def test_handle_try_start_when_already_playing_does_nothing(
        self,
        queue_repository: mock.Mock,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        track: Track = make_track()

        playback_service._transition_to(playback_state=PlaybackState.PLAYING, track=track)

        emit_finished: mock.Mock = mock.Mock()

        await playback_service.handle_try_start(
            guild_id=guild_id,
            emit_finished_event=emit_finished,
        )

        assert playback_service.state.is_playing is True
        assert playback_service.state.current_track is track

        emit_finished.assert_not_called()

        queue_repository.get.assert_not_called()
        queue_repository.save.assert_not_called()

        music_player.play.assert_not_awaited()
        music_player.stop.assert_not_awaited()

    async def test_handle_try_start_when_queue_empty_does_nothing(
        self,
        queue_repository: mock.Mock,
        music_player: mock.Mock,
        playback_service: PlaybackService,
    ) -> None:
        guild_id: int = 1

        queue_repository.get.return_value = Queue()

        emit_finished: mock.Mock = mock.Mock()

        await playback_service.handle_try_start(
            guild_id=guild_id, emit_finished_event=emit_finished
        )

        assert playback_service.state.is_idle is True
        assert playback_service.state.current_track is None

        emit_finished.assert_not_called()

        queue_repository.get.assert_called_once_with(guild_id)
        queue_repository.save.assert_not_called()

        music_player.play.assert_not_awaited()
        music_player.stop.assert_not_awaited()

    async def test_handle_try_start_dequeues_track_calls_player_play_and_sets_state_playing(
        self,
        queue_repository: mock.Mock,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        track: Track = make_track()

        q: Queue = Queue()
        q.enqueue(track)
        queue_repository.get.return_value = q

        emit_finished: mock.Mock = mock.Mock()

        await playback_service.handle_try_start(
            guild_id=guild_id,
            emit_finished_event=emit_finished,
        )

        assert playback_service.state.is_playing is True
        assert playback_service.state.current_track is track

        emit_finished.assert_not_called()

        queue_repository.get.assert_called_once_with(guild_id)
        queue_repository.save.assert_called_once_with(guild_id, q)

        music_player.play.assert_awaited_once()
        _, kwargs = music_player.play.await_args
        assert kwargs["context_id"] == guild_id
        assert kwargs["url"] == track.url
        assert callable(kwargs["on_finished"])
        music_player.stop.assert_not_awaited()

    async def test_handle_try_start_passes_after_callback_that_emits_track_finished_event(
        self,
        queue_repository: mock.Mock,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        track: Track = make_track()

        queue: Queue = Queue()
        queue.enqueue(track)
        queue_repository.get.return_value = queue

        done: asyncio.Event = asyncio.Event()
        emitted: list[TrackFinishedEvent] = []

        def emit_finished_event(finished_event: TrackFinishedEvent) -> None:
            emitted.append(finished_event)
            done.set()

        await playback_service.handle_try_start(
            guild_id=guild_id,
            emit_finished_event=emit_finished_event,
        )

        music_player.play.assert_awaited_once()
        _, kwargs = music_player.play.await_args
        assert kwargs["context_id"] == guild_id
        assert kwargs["url"] == track.url

        on_finished = kwargs["on_finished"]
        assert callable(on_finished)

        exc: RuntimeError = RuntimeError("boom")
        on_finished(guild_id, exc)

        await asyncio.wait_for(done.wait(), timeout=1)

        event: TrackFinishedEvent = emitted[0]
        assert event.guild_id == guild_id
        assert event.exception is exc

    async def test_handle_track_finished_transitions_to_idle_and_emits_try_start(
        self,
        queue_repository: mock.Mock,
        music_player: mock.Mock,
        playback_service: PlaybackService,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        playback_service._transition_to(playback_state=PlaybackState.PLAYING, track=make_track())

        events: Sequence[TryStartEvent] = await playback_service.handle_track_finished(
            TrackFinishedEvent(guild_id=guild_id, exception=None)
        )

        assert playback_service.state.is_idle is True
        assert playback_service.state.current_track is None
        assert list(events) == [TryStartEvent(guild_id=guild_id)]

        queue_repository.save.assert_not_called()
        queue_repository.delete.assert_not_called()

        music_player.play.assert_not_awaited()
        music_player.stop.assert_not_awaited()

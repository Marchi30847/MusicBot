from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Callable
from typing import Any, cast
from unittest import mock

import pytest
from tests.typing_helper import (
    MakeNowPlayingCommand,
    MakePlayUrlCommand,
    MakeSkipCommand,
    MakeStopCommand,
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
from music_bot.application.orchestration.music import GuildActor
from music_bot.application.orchestration.music.events import (
    TrackFinishedEvent,
    TryStartEvent,
)
from music_bot.application.orchestration.music.playback_service import PlaybackService
from music_bot.application.ports import MusicPlayer, QueueRepository


@pytest.fixture
def playback_service() -> mock.Mock:
    service: mock.Mock = mock.Mock(spec=PlaybackService)

    service.handle_play_url = mock.AsyncMock(
        return_value=(PlayUrlResult(queue_size=0, enqueued=True), [])
    )
    service.handle_stop = mock.AsyncMock(return_value=(StopResult(stopped=True, cleared=0), []))
    service.handle_skip = mock.AsyncMock(
        return_value=(SkipResult(skipped=False, now_playing=None), [])
    )
    service.handle_now_playing = mock.AsyncMock(
        return_value=(NowPlayingResult(is_playing=False, track=None), [])
    )

    service.handle_try_start = mock.AsyncMock(return_value=None)
    service.handle_track_finished = mock.AsyncMock(return_value=[])

    return service


@pytest.fixture
def actor(playback_service: mock.Mock) -> GuildActor:
    return GuildActor(
        playback_service=playback_service,
        queue_repository=cast(QueueRepository, mock.Mock(spec=QueueRepository)),
        music_player=cast(MusicPlayer, mock.Mock(spec=MusicPlayer)),
    )


@pytest.fixture
async def running_actor(actor: GuildActor) -> AsyncGenerator[GuildActor, Any]:
    actor.start()
    yield actor
    await actor.stop()


@pytest.mark.unit
@pytest.mark.asyncio
class TestGuildActor:
    async def test_start_twice_raises(self, actor: GuildActor) -> None:
        actor.start()

        try:
            with pytest.raises(RuntimeError):
                actor.start()
        finally:
            await actor.stop()

    async def test_send_request_when_not_started_raises(
        self,
        actor: GuildActor,
        make_play_url_command: MakePlayUrlCommand,
        make_stop_command: MakeStopCommand,
        make_skip_command: MakeSkipCommand,
        make_now_playing_command: MakeNowPlayingCommand,
    ) -> None:
        with pytest.raises(RuntimeError):
            await actor.send_play_url(make_play_url_command())
        with pytest.raises(RuntimeError):
            await actor.send_stop(make_stop_command())
        with pytest.raises(RuntimeError):
            await actor.send_skip(make_skip_command())
        with pytest.raises(RuntimeError):
            await actor.send_now_playing(make_now_playing_command())

    async def test_stop_when_not_started_is_noop(self, actor: GuildActor) -> None:
        await actor.stop()

    async def test_send_play_url_returns_result(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        command: PlayUrlCommand = make_play_url_command()

        expected_result: PlayUrlResult = PlayUrlResult(queue_size=1, enqueued=True)

        playback_service.handle_play_url.return_value = (expected_result, [])

        result: PlayUrlResult = await running_actor.send_play_url(command)

        assert result == expected_result

        playback_service.handle_play_url.assert_awaited_once_with(command)

    async def test_send_stop_returns_result(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_stop_command: MakeStopCommand,
    ) -> None:
        command: StopCommand = make_stop_command()

        expected_result: StopResult = StopResult(stopped=True, cleared=5)

        playback_service.handle_stop.return_value = (expected_result, [])

        result: StopResult = await running_actor.send_stop(command)

        assert result == expected_result

        playback_service.handle_stop.assert_awaited_once_with(command)

    async def test_send_skip_returns_result(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_skip_command: MakeSkipCommand,
    ) -> None:
        command: SkipCommand = make_skip_command()

        expected_result: SkipResult = SkipResult(skipped=True, now_playing=None)

        playback_service.handle_skip.return_value = (expected_result, [])

        result: SkipResult = await running_actor.send_skip(command)

        assert result == expected_result

        playback_service.handle_skip.assert_awaited_once_with(command)

    async def test_send_now_playing_returns_result(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_now_playing_command: MakeNowPlayingCommand,
    ) -> None:
        command: NowPlayingCommand = make_now_playing_command()

        expected_result: NowPlayingResult = NowPlayingResult(is_playing=True, track=None)

        playback_service.handle_now_playing.return_value = (expected_result, [])

        result: NowPlayingResult = await running_actor.send_now_playing(command)

        assert result == expected_result

        playback_service.handle_now_playing.assert_awaited_once_with(command)

    async def test_play_url_enqueues_try_start_event(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        guild_id: int = 1

        command: PlayUrlCommand = make_play_url_command(guild_id=guild_id)

        playback_service.handle_play_url.return_value = (
            PlayUrlResult(queue_size=1, enqueued=True),
            [TryStartEvent(guild_id=guild_id)],
        )

        await running_actor.send_play_url(command)

        await running_actor._mailbox.join()

        playback_service.handle_play_url.assert_awaited_once()
        _, kwargs = playback_service.handle_try_start.await_args
        assert kwargs["guild_id"] == guild_id

    async def test_skip_enqueues_try_start_event(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_skip_command: MakeSkipCommand,
    ) -> None:
        guild_id: int = 1

        command: SkipCommand = make_skip_command(guild_id=guild_id)

        playback_service.handle_skip.return_value = (
            SkipResult(skipped=True, now_playing=None),
            [TryStartEvent(guild_id=guild_id)],
        )

        await running_actor.send_skip(command)

        await running_actor._mailbox.join()

        playback_service.handle_skip.assert_awaited_once()
        _, kwargs = playback_service.handle_try_start.await_args
        assert kwargs["guild_id"] == guild_id

    async def test_track_finished_enqueues_try_start_event_via_emit_finished(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        guild_id: int = 1
        command: PlayUrlCommand = make_play_url_command(guild_id=guild_id)

        playback_service.handle_play_url.return_value = (
            PlayUrlResult(queue_size=1, enqueued=True),
            [TryStartEvent(guild_id=guild_id)],
        )
        playback_service.handle_track_finished.return_value = [TryStartEvent(guild_id=guild_id)]
        playback_service.handle_try_start.return_value = None

        await running_actor.send_play_url(command)
        await asyncio.wait_for(running_actor._mailbox.join(), timeout=1)

        assert playback_service.handle_try_start.await_count == 1

        first_call = playback_service.handle_try_start.await_args_list[0]
        emit_finished: Callable[[TrackFinishedEvent], None] = first_call.kwargs[
            "emit_finished_event"
        ]

        emit_finished(TrackFinishedEvent(guild_id=guild_id, exception=None))
        await asyncio.wait_for(running_actor._mailbox.join(), timeout=1)

        playback_service.handle_track_finished.assert_awaited_once_with(
            TrackFinishedEvent(guild_id=guild_id, exception=None)
        )
        assert playback_service.handle_try_start.await_count == 2

        calls = playback_service.handle_try_start.await_args_list
        assert calls[0].kwargs["guild_id"] == guild_id
        assert calls[1].kwargs["guild_id"] == guild_id

    async def test_try_start_event_calls_service_try_start(
        self,
        playback_service: mock.Mock,
        running_actor: GuildActor,
    ) -> None:
        guild_id: int = 1

        playback_service.handle_try_start.return_value = None

        running_actor._mailbox.put_nowait(TryStartEvent(guild_id=guild_id))
        await asyncio.wait_for(running_actor._mailbox.join(), timeout=1)

        playback_service.handle_try_start.assert_awaited_once()
        _, kwargs = playback_service.handle_try_start.await_args
        assert kwargs["guild_id"] == guild_id
        assert callable(kwargs["emit_finished_event"])

    async def test_track_finished_event_calls_service_track_finished(
        self, playback_service: mock.Mock, running_actor: GuildActor
    ) -> None:
        track_finished_event: TrackFinishedEvent = TrackFinishedEvent(guild_id=1, exception=None)

        playback_service.handle_track_finished.return_value = []

        running_actor._mailbox.put_nowait(track_finished_event)
        await asyncio.wait_for(running_actor._mailbox.join(), timeout=1)

        playback_service.handle_track_finished.assert_awaited_once_with(track_finished_event)

    async def test_service_exception_in_request_becomes_future_exception(
        self,
        playback_service: mock.Mock,
        running_actor,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        command: PlayUrlCommand = make_play_url_command()

        boom: RuntimeError = RuntimeError("boom")

        playback_service.handle_play_url.side_effect = boom

        with pytest.raises(RuntimeError) as excinfo:
            await running_actor.send_play_url(command)

        assert excinfo.value is boom

        playback_service.handle_play_url.assert_awaited_once_with(command)

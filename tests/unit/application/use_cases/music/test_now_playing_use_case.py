from __future__ import annotations

from unittest import mock

import pytest
from tests.typing_helper import MakeNowPlayingCommand, MakeTrack

from music_bot.application.contracts.commands.music import NowPlayingCommand
from music_bot.application.contracts.results.music import NowPlayingResult
from music_bot.application.mappers.music import map_track_to_dto
from music_bot.application.use_cases.music import NowPlayingUseCase


@pytest.mark.unit
@pytest.mark.asyncio
class TestNowPlayingUseCase:
    async def test_now_playing_calls_actor_and_returns_result(
        self, make_now_playing_command: MakeNowPlayingCommand, make_track: MakeTrack
    ) -> None:
        expected_result: NowPlayingResult = NowPlayingResult(
            is_playing=True, track=map_track_to_dto(make_track())
        )

        actor: mock.Mock = mock.Mock()
        actor.send_now_playing = mock.AsyncMock(return_value=expected_result)

        manager: mock.Mock = mock.Mock()
        manager.get_or_create = mock.Mock(return_value=actor)

        use_case = NowPlayingUseCase(manager)

        command: NowPlayingCommand = make_now_playing_command()

        result: NowPlayingResult = await use_case(command)

        assert result == expected_result

        manager.get_or_create.assert_called_once_with(1)
        actor.send_now_playing.assert_awaited_once_with(command)

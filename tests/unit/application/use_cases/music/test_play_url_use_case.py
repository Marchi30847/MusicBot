from __future__ import annotations

import unittest.mock as mock

import pytest
from tests.typing_helper import MakePlayUrlCommand

from music_bot.application.contracts.commands.music import PlayUrlCommand
from music_bot.application.contracts.results.music import PlayUrlResult
from music_bot.application.use_cases.music import PlayUrlUseCase


@pytest.mark.unit
@pytest.mark.asyncio
class TestPlayUrlUseCase:
    async def test_play_url_calls_actor_and_returns_result(
        self,
        make_play_url_command: MakePlayUrlCommand,
    ) -> None:
        expected_result: PlayUrlResult = PlayUrlResult(queue_size=5, enqueued=True)

        actor: mock.Mock = mock.Mock()
        actor.send_play_url = mock.AsyncMock(return_value=expected_result)

        manager: mock.Mock = mock.Mock()
        manager.get_or_create = mock.Mock(return_value=actor)

        use_case: PlayUrlUseCase = PlayUrlUseCase(manager)

        command: PlayUrlCommand = make_play_url_command(guild_id=1)

        result: PlayUrlResult = await use_case(command)

        assert result == expected_result

        manager.get_or_create.assert_called_once_with(1)
        actor.send_play_url.assert_awaited_once_with(command)

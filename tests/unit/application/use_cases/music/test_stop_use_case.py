from __future__ import annotations

from unittest import mock

import pytest
from tests.typing_helper import MakeStopCommand

from music_bot.application.contracts.commands.music import StopCommand
from music_bot.application.contracts.results.music import StopResult
from music_bot.application.use_cases.music import StopUseCase


@pytest.mark.unit
@pytest.mark.asyncio
class TestStopUseCase:
    async def test_stop_calls_actor_and_returns_result(
        self, make_stop_command: MakeStopCommand
    ) -> None:
        expected_result: StopResult = StopResult(stopped=True, cleared=5)

        actor: mock.Mock = mock.Mock()
        actor.send_stop = mock.AsyncMock(return_value=expected_result)

        manager: mock.Mock = mock.Mock()
        manager.get_or_create = mock.Mock(return_value=actor)

        use_case: StopUseCase = StopUseCase(manager)

        command: StopCommand = make_stop_command(guild_id=1)

        result: StopResult = await use_case(command)

        assert result == expected_result

        manager.get_or_create.assert_called_once_with(1)
        actor.send_stop.assert_awaited_once_with(command)

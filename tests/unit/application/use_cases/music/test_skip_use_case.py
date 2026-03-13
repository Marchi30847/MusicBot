from __future__ import annotations

from unittest import mock

import pytest
from tests.typing_helper import MakeSkipCommand

from music_bot.application.contracts.commands.music import SkipCommand
from music_bot.application.contracts.results.music import SkipResult
from music_bot.application.use_cases.music import SkipUseCase


@pytest.mark.unit
@pytest.mark.asyncio
class TestSkipUseCase:
    async def test_skip_calls_actor_and_returns_result(
        self, make_skip_command: MakeSkipCommand
    ) -> None:
        expected_result: SkipResult = SkipResult(skipped=True, now_playing=None)

        actor: mock.Mock = mock.Mock()
        actor.send_skip = mock.AsyncMock(return_value=expected_result)

        manager: mock.Mock = mock.Mock()
        manager.get_or_create = mock.Mock(return_value=actor)

        use_case: SkipUseCase = SkipUseCase(manager)

        command: SkipCommand = make_skip_command(guild_id=1)

        result: SkipResult = await use_case(command)

        assert result == expected_result

        manager.get_or_create.assert_called_once_with(1)
        actor.send_skip.assert_awaited_once_with(command)

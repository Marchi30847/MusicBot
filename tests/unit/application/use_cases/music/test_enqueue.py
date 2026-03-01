from __future__ import annotations

import pytest
from tests.typing_helper import MakeEnqueueCommand

from music_bot.application.contracts.commands.music import EnqueueCommand
from music_bot.application.contracts.results.music import EnqueueResult
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.application.use_cases.music import EnqueueUseCase


@pytest.fixture
def use_case(queue_repo: QueueRepository) -> EnqueueUseCase:
    return EnqueueUseCase(queue_repository=queue_repo)


@pytest.mark.unit
class TestEnqueueUseCase:
    def test_enqueue_to_empty_queue_returns_size_1(
        self,
        use_case: EnqueueUseCase,
        make_enqueue_command: MakeEnqueueCommand,
    ) -> None:
        cmd: EnqueueCommand = make_enqueue_command(
            guild_id=1,
            url="https://example.com/a.mp3",
            requested_by=123,
        )

        result: EnqueueResult = use_case.execute(cmd)

        assert result.queue_size == 1

    def test_enqueue_twice_in_same_guild_increments_size(
        self,
        use_case: EnqueueUseCase,
        make_enqueue_command: MakeEnqueueCommand,
    ) -> None:
        r1: EnqueueResult = use_case.execute(
            make_enqueue_command(guild_id=1, url="https://example.com/1.mp3", requested_by=1)
        )
        r2: EnqueueResult = use_case.execute(
            make_enqueue_command(guild_id=1, url="https://example.com/2.mp3", requested_by=1)
        )

        assert r1.queue_size == 1
        assert r2.queue_size == 2

    def test_queues_are_isolated_per_guild(
        self,
        use_case: EnqueueUseCase,
        make_enqueue_command: MakeEnqueueCommand,
    ) -> None:
        a1: EnqueueResult = use_case.execute(
            make_enqueue_command(guild_id=10, url="https://example.com/a1.mp3", requested_by=1)
        )
        b1: EnqueueResult = use_case.execute(
            make_enqueue_command(guild_id=20, url="https://example.com/b1.mp3", requested_by=1)
        )
        a2: EnqueueResult = use_case.execute(
            make_enqueue_command(guild_id=10, url="https://example.com/a2.mp3", requested_by=1)
        )

        assert a1.queue_size == 1
        assert b1.queue_size == 1
        assert a2.queue_size == 2

from __future__ import annotations

import pytest
from tests.typing_helper import MakeDequeueCommand, MakeTrack

from music_bot.application.contracts.commands.music import DequeueCommand
from music_bot.application.contracts.results.music import DequeueResult
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.application.use_cases.music import DequeueUseCase
from music_bot.domain.music.models import Queue, Track


@pytest.fixture
def use_case(queue_repo: QueueRepository) -> DequeueUseCase:
    return DequeueUseCase(queue_repository=queue_repo)


@pytest.mark.unit
class TestDequeueUseCase:
    def test_no_queue_returns_empty_result(
        self,
        use_case: DequeueUseCase,
        make_dequeue_command: MakeDequeueCommand,
    ) -> None:
        cmd: DequeueCommand = make_dequeue_command(guild_id=1, requested_by=123)

        result: DequeueResult = use_case.execute(cmd)

        assert result.queue_size == 0
        assert result.track is None

    def test_empty_queue_returns_empty_result(
        self,
        use_case: DequeueUseCase,
        queue_repo: QueueRepository,
        make_dequeue_command: MakeDequeueCommand,
    ) -> None:
        guild_id: int = 1
        queue_repo.get_or_create(guild_id)

        cmd: DequeueCommand = make_dequeue_command(guild_id=guild_id, requested_by=123)
        result: DequeueResult = use_case.execute(cmd)

        assert result.queue_size == 0
        assert result.track is None

    def test_dequeue_returns_first_track_and_decrements_size(
        self,
        use_case: DequeueUseCase,
        queue_repo: QueueRepository,
        make_dequeue_command: MakeDequeueCommand,
        make_track: MakeTrack,
    ) -> None:
        guild_id: int = 1

        t1: Track = make_track("https://example.com/1.mp3", requested_by=10)
        t2: Track = make_track("https://example.com/2.mp3", requested_by=20)

        queue: Queue = queue_repo.get_or_create(guild_id)
        queue.enqueue(t1)
        queue.enqueue(t2)
        queue_repo.save(guild_id, queue)

        cmd: DequeueCommand = make_dequeue_command(guild_id=guild_id, requested_by=999)
        result: DequeueResult = use_case.execute(cmd)

        assert result.queue_size == 1
        assert result.track is not None

        assert result.track.url == t1.url
        assert result.track.title == t1.title
        assert result.track.requested_by == t1.requested_by
        assert result.track.duration_seconds == t1.duration_seconds

        queue_after: Queue | None = queue_repo.get(guild_id)
        assert queue_after is not None
        assert queue_after.peek() == t2

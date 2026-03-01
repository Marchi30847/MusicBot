from __future__ import annotations

from datetime import UTC, datetime

import pytest

from music_bot.adapters.outbound.in_memory.music import InMemoryQueueRepository
from music_bot.application.contracts.commands.music import DequeueCommand, EnqueueCommand
from music_bot.application.ports.repositories.music import QueueRepository
from music_bot.domain.music.models import Queue, Track
from tests.typing_helper import MakeDequeueCommand, MakeEnqueueCommand, MakeTrack


@pytest.fixture
def queue() -> Queue:
    return Queue()


@pytest.fixture
def queue_repo() -> QueueRepository:
    return InMemoryQueueRepository()


@pytest.fixture
def make_track() -> MakeTrack:
    def _make_track(url: str, requested_by: int = 1) -> Track:
        return Track(
            url=url,
            title=url,
            requested_by=requested_by,
            requested_at=datetime.now(UTC),
            duration_seconds=0,
        )

    return _make_track


@pytest.fixture
def make_enqueue_command() -> MakeEnqueueCommand:
    def _make_enqueue_command(
        guild_id: int,
        url: str,
        requested_by: int,
        title: str | None = None,
    ) -> EnqueueCommand:
        return EnqueueCommand(
            guild_id=guild_id,
            url=url,
            requested_by=requested_by,
            title=title,
        )

    return _make_enqueue_command


@pytest.fixture
def make_dequeue_command() -> MakeDequeueCommand:
    def _make_dequeue_command(guild_id: int, requested_by: int) -> DequeueCommand:
        return DequeueCommand(
            guild_id=guild_id,
            requested_by=requested_by,
        )

    return _make_dequeue_command

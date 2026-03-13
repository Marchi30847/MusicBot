from __future__ import annotations

import pytest
from tests.typing_helper import MakeTrack

from music_bot.domain.music.models import Queue, Track


@pytest.fixture
def queue() -> Queue:
    return Queue()


@pytest.mark.unit
class TestQueue:
    def test_queue_empty_by_default(self, queue: Queue) -> None:
        assert len(queue) == 0
        assert bool(queue) is False
        assert queue.peek() is None
        assert queue.dequeue() is None

    def test_enqueue_increases_length(self, queue: Queue, make_track: MakeTrack) -> None:
        track: Track = make_track(url="https://example.com/a.mp3")

        queue.enqueue(track)

        assert len(queue) == 1
        assert bool(queue) is True
        assert queue.peek() == track

    def test_dequeue_fifo(self, queue: Queue, make_track: MakeTrack) -> None:
        first: Track = make_track(url="https://example.com/1.mp3", requested_by=1)
        second: Track = make_track(url="https://example.com/2.mp3", requested_by=2)

        queue.enqueue(first)
        queue.enqueue(second)

        assert queue.dequeue() == first
        assert queue.dequeue() == second
        assert queue.dequeue() is None
        assert len(queue) == 0

    def test_peek_does_not_remove(self, queue: Queue, make_track: MakeTrack) -> None:
        track: Track = make_track(url="https://example.com/a.mp3")
        queue.enqueue(track)

        assert queue.peek() == track
        assert len(queue) == 1
        assert queue.dequeue() == track
        assert len(queue) == 0

    def test_clear(self, queue: Queue, make_track: MakeTrack) -> None:
        queue.enqueue(make_track(url="https://example.com/1.mp3"))
        queue.enqueue(make_track(url="https://example.com/2.mp3"))

        queue.clear()

        assert len(queue) == 0
        assert bool(queue) is False
        assert queue.peek() is None

    def test_iter_order(self, queue: Queue, make_track: MakeTrack) -> None:
        tracks: list[Track] = [
            make_track(url="https://example.com/1.mp3"),
            make_track(url="https://example.com/2.mp3"),
            make_track(url="https://example.com/3.mp3"),
        ]
        for t in tracks:
            queue.enqueue(t)

        assert list(queue) == tracks

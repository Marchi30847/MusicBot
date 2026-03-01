from __future__ import annotations

from collections import deque
from collections.abc import Iterator

from .track import Track


class Queue:
    def __init__(self) -> None:
        self._items: deque[Track] = deque()

    def __repr__(self) -> str:
        return f"<Queue: {len(self._items)} tracks>"

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self) -> Iterator[Track]:
        return iter(self._items)

    def enqueue(self, track: Track) -> None:
        self._items.append(track)

    def dequeue(self) -> Track | None:
        try:
            return self._items.popleft()
        except IndexError:
            return None

    def peek(self) -> Track | None:
        try:
            return self._items[0]
        except IndexError:
            return None

    def clear(self) -> None:
        self._items.clear()

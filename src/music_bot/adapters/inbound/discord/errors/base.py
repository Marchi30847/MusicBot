from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiscordAdapterError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message

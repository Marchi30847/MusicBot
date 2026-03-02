from __future__ import annotations

from .base import DiscordAdapterError


class NotInGuildError(DiscordAdapterError):
    def __init__(self) -> None:
        super().__init__("This command can only be used in a server.")


class NotAMemberError(DiscordAdapterError):
    def __init__(self) -> None:
        super().__init__("This command can only be used by a server member.")

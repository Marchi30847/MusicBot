from __future__ import annotations

from .base import DiscordAdapterError
from .context import NotAMemberError, NotInGuildError
from .voice import (
    NotConnectedToVoiceError,
    NotInVoiceError,
    UnsupportedVoiceChannelError,
    VoiceConnectionError,
    VoiceForbiddenError,
    VoiceTimeoutError,
)

__all__ = (
    "DiscordAdapterError",
    "NotAMemberError",
    "NotConnectedToVoiceError",
    "NotInGuildError",
    "NotInVoiceError",
    "UnsupportedVoiceChannelError",
    "VoiceConnectionError",
    "VoiceForbiddenError",
    "VoiceTimeoutError",
)

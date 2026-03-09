from __future__ import annotations

from datetime import UTC, datetime

from music_bot.application.contracts.commands.music import PlayUrlCommand
from music_bot.domain.music.models import Track


def map_play_url_command_to_track(command: PlayUrlCommand) -> Track:
    return Track(
        url=command.url,
        title=command.title if command.title is not None else command.url,
        requested_by=command.requested_by,
        requested_at=datetime.now(UTC),
        duration_seconds=0,
    )

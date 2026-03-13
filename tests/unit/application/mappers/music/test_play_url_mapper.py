from __future__ import annotations

from datetime import UTC

import pytest
from tests.typing_helper import MakePlayUrlCommand

from music_bot.application.contracts.commands.music import PlayUrlCommand
from music_bot.application.mappers.music import map_play_url_command_to_track
from music_bot.domain.music.models import Track


@pytest.mark.unit
class TestPlayUrlMapper:
    def test_title_falls_back_to_url_when_missing(
        self, make_play_url_command: MakePlayUrlCommand
    ) -> None:
        url: str = "https://example.com/a.mp3"
        cmd: PlayUrlCommand = make_play_url_command(
            guild_id=1, url=url, requested_by=123, title=None
        )

        track: Track = map_play_url_command_to_track(cmd)

        assert track.url == url
        assert track.title == url

    def test_title_is_used_when_provided(self, make_play_url_command: MakePlayUrlCommand) -> None:
        url: str = "https://example.com/a.mp3"
        title: str = "My Track"
        cmd: PlayUrlCommand = make_play_url_command(
            guild_id=1, url=url, requested_by=123, title=title
        )

        track: Track = map_play_url_command_to_track(cmd)

        assert track.url == url
        assert track.title == title

    def test_sets_requested_by_duration_and_timestamp(
        self, make_play_url_command: MakePlayUrlCommand
    ) -> None:
        cmd: PlayUrlCommand = make_play_url_command(
            guild_id=1, url="https://example.com/a.mp3", requested_by=999, title="X"
        )

        track: Track = map_play_url_command_to_track(cmd)

        assert track.requested_by == 999
        assert track.duration_seconds == 0
        assert track.requested_at.tzinfo == UTC

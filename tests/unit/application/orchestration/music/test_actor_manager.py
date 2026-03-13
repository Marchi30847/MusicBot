from __future__ import annotations

from typing import cast
from unittest import mock
from unittest.mock import patch

import pytest

from music_bot.application.orchestration.music import MusicActorManager
from music_bot.application.ports import MusicPlayer, QueueRepository


@pytest.fixture
def actor_manager() -> MusicActorManager:
    return MusicActorManager(
        queue_repository=cast(QueueRepository, mock.Mock(spec=QueueRepository)),
        music_player=cast(MusicPlayer, mock.Mock(spec=MusicPlayer)),
    )


@pytest.mark.unit
class TestActorManager:
    @patch("music_bot.application.orchestration.music.manager.GuildActor")
    def test_get_or_create_creates_new_actor(
        self,
        mock_guild_actor_class: mock.Mock,
        actor_manager: MusicActorManager,
    ) -> None:
        fake_actor: mock.Mock = mock.Mock()
        fake_actor.start = mock.Mock()

        mock_guild_actor_class.return_value = fake_actor

        actor = actor_manager.get_or_create(1)

        assert actor is fake_actor
        assert actor_manager.get(1) is fake_actor

        mock_guild_actor_class.assert_called_once()
        fake_actor.start.assert_called_once()

    @patch("music_bot.application.orchestration.music.manager.GuildActor")
    def test_get_or_create_returns_same_actor_and_does_not_start_twice(
        self,
        mock_guild_actor_class: mock.Mock,
        actor_manager: MusicActorManager,
    ) -> None:
        fake_actor: mock.Mock = mock.Mock()
        fake_actor.start = mock.Mock()

        mock_guild_actor_class.return_value = fake_actor

        actor1 = actor_manager.get_or_create(1)
        actor2 = actor_manager.get_or_create(1)

        assert actor1 is actor2
        assert actor_manager.get(1) is actor1

        mock_guild_actor_class.assert_called_once()
        fake_actor.start.assert_called_once()

    def test_get_returns_none_when_missing(self, actor_manager: MusicActorManager) -> None:
        assert actor_manager.get(1) is None

    @patch("music_bot.application.orchestration.music.manager.GuildActor")
    @pytest.mark.asyncio
    async def test_stop_does_nothing_when_missing(
        self,
        mock_guild_actor_class: mock.Mock,
        actor_manager: MusicActorManager,
    ) -> None:
        fake_actor: mock.Mock = mock.Mock()
        fake_actor.start = mock.Mock()
        fake_actor.stop = mock.AsyncMock(return_value=None)

        mock_guild_actor_class.return_value = fake_actor

        actor_manager.get_or_create(1)

        await actor_manager.stop(2)

        assert actor_manager.get(2) is None

        fake_actor.stop.assert_not_awaited()

    @patch("music_bot.application.orchestration.music.manager.GuildActor")
    @pytest.mark.asyncio
    async def test_stop_awaits_actor_stop_but_keeps_actor(
        self,
        mock_guild_actor_class: mock.Mock,
        actor_manager: MusicActorManager,
    ) -> None:
        fake_actor: mock.Mock = mock.Mock()
        fake_actor.start = mock.Mock()
        fake_actor.stop = mock.AsyncMock(return_value=None)

        mock_guild_actor_class.return_value = fake_actor

        actor_manager.get_or_create(1)

        await actor_manager.stop(1)

        assert actor_manager.get(1) is fake_actor

        fake_actor.stop.assert_awaited_once()

    @patch("music_bot.application.orchestration.music.manager.GuildActor")
    @pytest.mark.asyncio
    async def test_stop_and_remove_awaits_stop_and_removes_actor(
        self,
        mock_guild_actor_class: mock.Mock,
        actor_manager: MusicActorManager,
    ) -> None:
        fake_actor: mock.Mock = mock.Mock()
        fake_actor.start = mock.Mock()
        fake_actor.stop = mock.AsyncMock(return_value=None)

        mock_guild_actor_class.return_value = fake_actor

        actor_manager.get_or_create(1)

        await actor_manager.stop_and_remove(1)

        assert actor_manager.get(1) is None

        fake_actor.stop.assert_awaited_once()

    @patch("music_bot.application.orchestration.music.manager.GuildActor")
    @pytest.mark.asyncio
    async def test_shutdown_stops_all_actors_and_clears_registry(
        self,
        mock_guild_actor_class: mock.Mock,
        actor_manager: MusicActorManager,
    ) -> None:
        a1: mock.Mock = mock.Mock()
        a1.start = mock.Mock()
        a1.stop = mock.AsyncMock(return_value=None)

        a2: mock.Mock = mock.Mock()
        a2.start = mock.Mock()
        a2.stop = mock.AsyncMock(return_value=None)

        mock_guild_actor_class.side_effect = [a1, a2]

        actor_manager.get_or_create(1)
        actor_manager.get_or_create(2)

        await actor_manager.shutdown()

        assert actor_manager.get(1) is None
        assert actor_manager.get(2) is None

        a1.stop.assert_awaited_once()
        a2.stop.assert_awaited_once()

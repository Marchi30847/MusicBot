from __future__ import annotations

import discord
from discord import Interaction, app_commands
from discord.ext import commands

from music_bot.adapters.inbound.discord.cogs.base import BaseCog
from music_bot.adapters.inbound.discord.helpers import (
    ensure_voice_connected,
    require_guild,
    require_member,
    require_voice_connected,
)
from music_bot.adapters.inbound.discord.ui import Responder
from music_bot.application.contracts.commands.music import (
    NowPlayingCommand,
    PlayUrlCommand,
    SkipCommand,
    StopCommand,
)
from music_bot.application.contracts.results.music import (
    NowPlayingResult,
    PlayUrlResult,
    SkipResult,
    StopResult,
)

from .deps import PlaybackDependencies


class PlaybackCog(BaseCog, name="Playback"):
    def __init__(self, bot: commands.Bot, deps: PlaybackDependencies) -> None:
        super().__init__(bot)
        self.deps: PlaybackDependencies = deps

    @app_commands.command(name="play", description="Plays a track")
    @app_commands.describe(url="The URL of the track to play")
    async def play(self, interaction: Interaction, url: str) -> None:
        responder: Responder = Responder(interaction)

        guild: discord.Guild = require_guild(interaction)
        member: discord.Member = require_member(interaction)

        await responder.defer()

        await ensure_voice_connected(guild=guild, member=member)

        result: PlayUrlResult = await self.deps.play_url(
            PlayUrlCommand(
                guild_id=guild.id,
                url=url,
                requested_by=member.id,
                title=url,
            )
        )

        await responder.success(f"Playing {result.enqueued}")

    @app_commands.command(name="pause", description="Pauses the current track")
    async def pause(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="resume", description="Resumes the current track")
    async def resume(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="skip", description="Skips the current track")
    async def skip(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        guild: discord.Guild = require_guild(interaction)
        member: discord.Member = require_member(interaction)

        await responder.defer()

        require_voice_connected(guild)

        result: SkipResult = await self.deps.skip(
            SkipCommand(
                guild_id=guild.id,
                requested_by=member.id,
            )
        )

        await responder.success(f"Skipped {result.skipped}")

    @app_commands.command(name="stop", description="Stops the current track and clears the queue")
    async def stop(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        guild: discord.Guild = require_guild(interaction)
        member: discord.Member = require_member(interaction)

        await responder.defer()

        require_voice_connected(guild)

        result: StopResult = await self.deps.stop(
            StopCommand(
                guild_id=guild.id,
                requested_by=member.id,
            )
        )

        await responder.success(f"Stopped {result.cleared} tracks")

    @app_commands.command(name="queue", description="Shows the current queue")
    async def queue(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="nowplaying", description="Shows the currently playing track")
    async def now_playing(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        guild: discord.Guild = require_guild(interaction)
        member: discord.Member = require_member(interaction)

        await responder.defer()

        result: NowPlayingResult = await self.deps.now_playing(
            NowPlayingCommand(
                guild_id=guild.id,
                requested_by=member.id,
            )
        )

        await responder.success(f"Now playing {result.track}")

    @app_commands.command(name="shuffle", description="Shuffles the queue")
    async def shuffle(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="loop", description="Loops the current track")
    async def loop(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="volume", description="Sets the volume of the current track")
    async def volume(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(
        name="seek", description="Seeks to a specific position in the current track"
    )
    async def seek(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="remove", description="Removes a track from the queue")
    async def remove(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="playlist", description="Plays a playlist")
    async def playlist(self, interaction: Interaction) -> None:
        pass

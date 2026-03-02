from __future__ import annotations

from discord import Interaction, app_commands
from discord.ext import commands

from .base import BaseCog


class PlaybackCog(BaseCog, name="Playback"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    @app_commands.command(name="play", description="Plays a track")
    async def play(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="pause", description="Pauses the current track")
    async def pause(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="resume", description="Resumes the current track")
    async def resume(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="skip", description="Skips the current track")
    async def skip(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="stop", description="Stops the current track and clears the queue")
    async def stop(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="queue", description="Shows the current queue")
    async def queue(self, interaction: Interaction) -> None:
        pass

    @app_commands.command(name="nowplaying", description="Shows the currently playing track")
    async def now_playing(self, interaction: Interaction) -> None:
        pass

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

from __future__ import annotations

from discord import Interaction, app_commands
from discord.ext import commands

from music_bot.adapters.inbound.discord.cogs.base import BaseCog
from music_bot.adapters.inbound.discord.ui import Responder


class PingCog(BaseCog, name="Ping"):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot)

    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        latency_ms: float = self.bot.latency * 1000
        await responder.success(f"Pong! {latency_ms:.0f}ms")

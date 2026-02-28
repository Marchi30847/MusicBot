from __future__ import annotations

from discord import Interaction, app_commands
from discord.ext import commands


class PingCog(commands.Cog, name="Ping"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: Interaction) -> None:
        latency_ms: float = self.bot.latency * 1000
        await interaction.response.send_message(f"Pong! {latency_ms:.0f}ms")

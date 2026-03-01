from __future__ import annotations

import logging

import discord
from discord import Interaction

from .formatter import format_error, format_info, format_success

logger: logging.Logger = logging.getLogger(__name__)


class Responder:
    def __init__(self, interaction: Interaction) -> None:
        self._interaction: Interaction = interaction

    async def defer(self, *, ephemeral: bool = True) -> None:
        if self._interaction.response.is_done():
            logger.debug("Interaction response already done; skip defer")
            return

        try:
            await self._interaction.response.defer(ephemeral=ephemeral)
        except (discord.InteractionResponded, discord.NotFound, discord.HTTPException) as exc:
            logger.warning(f"Failed to defer _interaction: {exc}")

    async def success(
        self, message: str, *, title: str | None = None, ephemeral: bool = False
    ) -> None:
        embed: discord.Embed = (
            format_success(message) if title is None else format_success(message, title=title)
        )
        await self._send(embed, ephemeral=ephemeral)

    async def info(self, message: str, *, title: str | None = None, ephemeral: bool = True) -> None:
        embed: discord.Embed = (
            format_info(message) if title is None else format_info(message, title=title)
        )
        await self._send(embed, ephemeral=ephemeral)

    async def error(
        self, message: str, *, title: str | None = None, ephemeral: bool = True
    ) -> None:
        embed: discord.Embed = (
            format_error(message) if title is None else format_error(message, title=title)
        )
        await self._send(embed, ephemeral=ephemeral)

    async def _send(self, embed: discord.Embed, *, ephemeral: bool) -> None:
        try:
            if not self._interaction.response.is_done():
                await self._interaction.response.send_message(embed=embed, ephemeral=ephemeral)
                return

            await self._interaction.followup.send(embed=embed, ephemeral=ephemeral)
        except (discord.InteractionResponded, discord.NotFound, discord.HTTPException) as exc:
            logger.warning(f"Failed to send message: {exc}")

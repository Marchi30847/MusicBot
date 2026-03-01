from __future__ import annotations

from typing import cast

import discord
from discord import Interaction, Member, VoiceChannel, VoiceProtocol, app_commands
from discord.abc import Connectable
from discord.ext import commands

from music_bot.adapters.inbound.discord.ui import Responder


class VoiceCog(commands.Cog, name="Voice"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @app_commands.command(name="join", description="Joins a voice channel")
    async def join(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        if interaction.guild is None:
            await responder.error("This command can only be used in a server.")
            return

        member: Member | None = interaction.user if isinstance(interaction.user, Member) else None
        if member is None or member.voice is None or member.voice.channel is None:
            await responder.error("You must be in a voice channel to use this command.")
            return

        channel: Connectable = member.voice.channel
        if not isinstance(channel, VoiceChannel):
            await responder.error("I can only join standard voice channels.")
            return

        voice_client: VoiceProtocol | None = interaction.guild.voice_client
        if voice_client is not None and voice_client.channel == channel:
            await responder.info("I'm already in that channel.")
            return

        await responder.defer()

        if voice_client is not None:
            try:
                await cast(discord.VoiceClient, voice_client).move_to(channel)
            except TimeoutError:
                await responder.error("Voice connection timed out. Please try again.")
                return
            except discord.Forbidden:
                await responder.error("I don't have permission to move to that channel.")
                return
            except discord.ClientException as exc:
                await responder.error(f"An error {exc} occurred while moving to the voice channel.")
                return

            await responder.success(f"Moved to {channel.mention}")
            return

        try:
            await channel.connect()
        except TimeoutError:
            await responder.error("Voice connection timed out. Please try again.")
            return
        except discord.Forbidden:
            await responder.error("I don't have permission to join that channel.")
            return
        except discord.ClientException as exc:
            await responder.error(f"An error {exc} occurred while connecting to the voice channel.")
            return

        await responder.success(f"Connected to {channel.mention}")

    @app_commands.command(name="leave", description="Leaves the current voice channel")
    async def leave(self, interaction: Interaction) -> None:
        responder: Responder = Responder(interaction)

        if interaction.guild is None:
            await responder.error("This command can only be used in a server.")
            return

        voice_client: VoiceProtocol | None = interaction.guild.voice_client
        if voice_client is None:
            await responder.error("I'm not in a voice channel.")
            return

        await responder.defer()

        channel: Connectable = voice_client.channel
        try:
            await voice_client.disconnect(force=False)
        except discord.ClientException as exc:
            await responder.error(
                f"An error {exc} occurred while disconnecting from the voice channel."
            )
            return

        label: str
        if isinstance(channel, VoiceChannel):
            label = channel.mention
        else:
            label = "the voice channel"

        await responder.success(f"Disconnected from {label}")

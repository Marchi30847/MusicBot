from __future__ import annotations

from typing import cast

import discord
from discord import Interaction, Member, VoiceChannel, VoiceProtocol, app_commands
from discord.abc import Connectable
from discord.ext import commands


class VoiceCog(commands.Cog, name="Voice"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @app_commands.command(name="join", description="Joins a voice channel")
    async def join(self, interaction: Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        member: Member | None = interaction.user if isinstance(interaction.user, Member) else None
        if member is None or member.voice is None or member.voice.channel is None:
            await interaction.response.send_message(
                "You must be in a voice channel to use this command.",
                ephemeral=True,
            )
            return

        channel: Connectable = member.voice.channel
        if not isinstance(channel, VoiceChannel):
            await interaction.response.send_message(
                "I can only join standard voice channels.",
                ephemeral=True,
            )
            return

        voice_client: VoiceProtocol | None = interaction.guild.voice_client
        if voice_client is not None and voice_client.channel == channel:
            await interaction.response.send_message(
                "I'm already in that channel.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        if voice_client is not None:
            try:
                await cast(discord.VoiceClient, voice_client).move_to(channel)
            except TimeoutError:
                await interaction.followup.send(
                    "Voice connection timed out. Please try again.",
                    ephemeral=True,
                )
                return
            except discord.Forbidden:
                await interaction.followup.send(
                    "I don't have permission to move to that channel.",
                    ephemeral=True,
                )
                return
            except discord.ClientException as exc:
                await interaction.followup.send(
                    f"An error {exc} occurred while moving to the voice channel.",
                    ephemeral=True,
                )
                return

            await interaction.followup.send(
                f"Moved to {channel.mention}",
                ephemeral=True,
            )
            return

        try:
            await channel.connect()
        except TimeoutError:
            await interaction.followup.send(
                "Voice connection timed out. Please try again.",
                ephemeral=True,
            )
            return
        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to join that channel.",
                ephemeral=True,
            )
            return
        except discord.ClientException as exc:
            await interaction.followup.send(
                f"An error {exc} occurred while connecting to the voice channel.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"Connected to {channel.mention}",
            ephemeral=True,
        )

    @app_commands.command(name="leave", description="Leaves the current voice channel")
    async def leave(self, interaction: Interaction) -> None:
        if interaction.guild is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        voice_client: VoiceProtocol | None = interaction.guild.voice_client
        if voice_client is None:
            await interaction.response.send_message(
                "I'm not in a voice channel.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        channel: Connectable = voice_client.channel
        try:
            await voice_client.disconnect(force=False)
        except discord.ClientException as exc:
            await interaction.followup.send(
                f"An error {exc} occurred while disconnecting from the voice channel.",
                ephemeral=True,
            )
            return

        label: str
        if isinstance(channel, VoiceChannel):
            label = channel.mention
        else:
            label = "the voice channel"

        await interaction.followup.send(
            f"Disconnected from {label}",
            ephemeral=True,
        )

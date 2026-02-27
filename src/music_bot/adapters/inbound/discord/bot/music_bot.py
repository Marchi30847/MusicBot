from __future__ import annotations

from discord import AllowedMentions, ClientUser, Intents
from discord.ext import commands


class MusicBot(commands.Bot):
    def __init__(self, *, intents: Intents, dependencies: object | None = None) -> None:
        allowed_mentions: AllowedMentions = AllowedMentions(
            everyone=False,
            roles=False,
            users=False,
            replied_user=False,
        )
        super().__init__(command_prefix="!", intents=intents, allowed_mentions=allowed_mentions)
        self.dependencies: object | None = dependencies

    async def setup_hook(self) -> None:
        await super().setup_hook()
        return

    async def on_ready(self) -> None:
        user: ClientUser | None = self.user

        if user is None:
            print("Logged in, but user is not available yet.")
            return

        print(f"Logged in as {user} (ID: {user.id})")

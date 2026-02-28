from __future__ import annotations

import asyncio

from music_bot.bootstrap.discord import run_discord_bot
from music_bot.bootstrap.logging import configure_logging
from music_bot.bootstrap.settings import Settings, SettingsLoadError, load_settings


async def main() -> None:
    try:
        settings: Settings = load_settings()
    except SettingsLoadError as exc:
        raise SystemExit(str(exc)) from exc

    configure_logging(settings)

    await run_discord_bot(settings)


if __name__ == "__main__":
    asyncio.run(main())

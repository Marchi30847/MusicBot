from __future__ import annotations

from typing import ClassVar

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from music_bot.bootstrap.settings.types import LogLevel


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="ignore", case_sensitive=True
    )

    discord_token: SecretStr = Field(alias="DISCORD_TOKEN")
    discord_guild_id: int | None = Field(default=None, alias="DISCORD_GUILD_ID")
    database_url: PostgresDsn = Field(alias="DATABASE_URL")
    log_level: LogLevel = Field(default=LogLevel.INFO, alias="LOG_LEVEL")

    @field_validator("discord_token")
    @classmethod
    def validate_discord_token(cls, value: SecretStr) -> SecretStr:
        token: str = value.get_secret_value().strip()
        if not token:
            raise ValueError("Discord token cannot be empty")

        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_logging_level(cls, value: object) -> LogLevel:
        if isinstance(value, str):
            normalized: str = value.strip().upper()
            return LogLevel(normalized)
        if isinstance(value, LogLevel):
            return value

        raise TypeError(f"LOG_LEVEL must be a string, got {type(value).__name__}")

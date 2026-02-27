from __future__ import annotations

from typing import ClassVar

from pydantic import Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        extra="ignore", case_sensitive=True
    )

    discord_token: SecretStr = Field(alias="DISCORD_TOKEN")
    discord_guild_id: int | None = Field(default=None, alias="DISCORD_GUILD_ID")
    database_url: PostgresDsn = Field(alias="DATABASE_URL")

    @field_validator("discord_token")
    @classmethod
    def validate_discord_token(cls, value: SecretStr) -> SecretStr:
        token: str = value.get_secret_value().strip()
        if not token:
            raise ValueError("Discord token cannot be empty")

        return value

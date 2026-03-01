from __future__ import annotations

from pydantic import BaseModel, Field


class EnqueueCommand(BaseModel):
    url: str = Field(..., min_length=1)
    requested_by: int = Field(..., gt=0)
    guild_id: int = Field(..., gt=0)
    title: str | None = Field(default=None)

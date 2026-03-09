from __future__ import annotations

from pydantic import BaseModel, Field


class SkipCommand(BaseModel):
    guild_id: int = Field(..., gt=0)
    requested_by: int = Field(..., gt=0)

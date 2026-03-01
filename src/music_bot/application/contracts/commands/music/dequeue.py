from __future__ import annotations

from pydantic import BaseModel, Field


class DequeueCommand(BaseModel):
    requested_by: int = Field(..., gt=0)
    guild_id: int = Field(..., gt=0)

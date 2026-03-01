from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Track(BaseModel):
    url: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    requested_by: int = Field(..., gt=0)
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_seconds: int = Field(..., ge=0)

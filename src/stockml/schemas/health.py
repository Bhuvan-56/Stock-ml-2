"""API schemas for service health responses."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Response model for backend health checks."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: str
    environment: str
    version: str
    timestamp: datetime

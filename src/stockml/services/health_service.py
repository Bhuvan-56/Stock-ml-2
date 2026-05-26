"""Application service for backend health checks."""

from __future__ import annotations

from datetime import datetime, timezone

from stockml import __version__
from stockml.core.config import Settings
from stockml.schemas.health import HealthResponse


class HealthService:
    """Provide health metadata without coupling routes to settings internals."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def get_status(self) -> HealthResponse:
        """Return the current health payload for the API."""

        return HealthResponse(
            status="ok",
            service=self._settings.app_name,
            environment=self._settings.environment,
            version=__version__,
            timestamp=datetime.now(timezone.utc),
        )

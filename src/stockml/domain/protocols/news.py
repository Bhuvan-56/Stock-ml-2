"""Protocol for contextual market news search providers."""

from __future__ import annotations

from typing import Protocol

from stockml.domain.models import DailyNewsSearchRequest, NewsArticle


class NewsSearchProvider(Protocol):
    """Search market news for a specific trading day."""

    provider_name: str

    def search_daily_news(
        self, request: DailyNewsSearchRequest
    ) -> tuple[NewsArticle, ...]:
        """Return normalized news results for a daily market context lookup."""

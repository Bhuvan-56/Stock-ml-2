"""Application service for anomaly-related market news lookups."""

from __future__ import annotations

from datetime import date

from stockml.core.config import NewsSettings
from stockml.domain.models import DailyNewsSearchRequest, NewsArticle
from stockml.domain.protocols import NewsSearchProvider


class NewsService:
    """Search for same-day market news around large model misses."""

    def __init__(
        self,
        *,
        settings: NewsSettings,
        provider: NewsSearchProvider | None,
    ) -> None:
        self._settings = settings
        self._provider = provider

    @property
    def is_enabled(self) -> bool:
        """Return whether contextual news search is available."""

        return self._settings.enabled and self._provider is not None

    @property
    def provider_name(self) -> str | None:
        """Return the active news provider name, if any."""

        if self._provider is None:
            return None
        return self._provider.provider_name

    @property
    def max_anomaly_days(self) -> int:
        """Return the maximum number of anomaly days to enrich."""

        return self._settings.max_anomaly_days

    def search_market_news(
        self,
        *,
        symbol: str,
        trade_date: date,
    ) -> tuple[NewsArticle, ...]:
        """Return same-day market news for a ticker if the provider is enabled."""

        if not self.is_enabled or self._provider is None:
            return ()

        request = DailyNewsSearchRequest(
            query=f"{symbol} stock news {trade_date.isoformat()}",
            trade_date=trade_date,
            max_results=self._settings.max_articles_per_anomaly,
        )
        return self._provider.search_daily_news(request)

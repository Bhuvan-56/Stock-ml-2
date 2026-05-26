"""Tavily-backed news provider for anomaly context."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from stockml.core.config import NewsSettings
from stockml.core.exceptions import UpstreamServiceError
from stockml.domain.models import DailyNewsSearchRequest, NewsArticle


class TavilyNewsProvider:
    """Retrieve daily stock news context through Tavily's search API."""

    provider_name = "tavily"
    _endpoint = "https://api.tavily.com/search"

    def __init__(self, settings: NewsSettings) -> None:
        if not settings.has_api_key:
            raise ValueError("A Tavily API key is required to enable news search.")

        self._settings = settings
        self._api_key = settings.tavily_api_key.get_secret_value()

    def search_daily_news(
        self, request: DailyNewsSearchRequest
    ) -> tuple[NewsArticle, ...]:
        """Return normalized Tavily news results for the requested trading day."""

        payload = {
            "api_key": self._api_key,
            "query": request.query,
            "topic": "news",
            "max_results": min(
                request.max_results,
                self._settings.max_articles_per_anomaly,
            ),
            "start_date": request.trade_date.isoformat(),
            "end_date": (request.trade_date + timedelta(days=1)).isoformat(),
        }
        request_body = json.dumps(payload).encode("utf-8")
        http_request = Request(
            self._endpoint,
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(
                http_request,
                timeout=self._settings.request_timeout_seconds,
            ) as response:
                response_body = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = self._extract_error_detail(exc)
            raise UpstreamServiceError(
                f"Tavily news search failed: {detail}"
            ) from exc
        except URLError as exc:
            raise UpstreamServiceError(
                "Tavily news search could not be reached."
            ) from exc

        try:
            payload = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise UpstreamServiceError(
                "Tavily news search returned an unreadable response."
            ) from exc

        raw_results = payload.get("results", [])
        if not isinstance(raw_results, list):
            raise UpstreamServiceError(
                "Tavily news search returned an unexpected results payload."
            )

        articles: list[NewsArticle] = []
        for raw_result in raw_results[: request.max_results]:
            if not isinstance(raw_result, dict):
                continue

            title = str(raw_result.get("title") or "").strip()
            url = str(raw_result.get("url") or "").strip()
            if not title or not url:
                continue

            source = self._extract_source(raw_result, url)
            summary = str(raw_result.get("content") or "").strip() or None
            articles.append(
                NewsArticle(
                    title=title,
                    url=url,
                    source=source,
                    summary=summary,
                    published_at=self._parse_published_at(
                        raw_result.get("published_date")
                    ),
                )
            )

        return tuple(articles)

    @staticmethod
    def _extract_error_detail(error: HTTPError) -> str:
        """Return the most useful HTTP error detail from a Tavily response."""

        try:
            payload = json.loads(error.read().decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return f"HTTP {error.code}"

        if isinstance(payload, dict):
            detail = payload.get("detail") or payload.get("message")
            if isinstance(detail, str) and detail.strip():
                return detail.strip()

        return f"HTTP {error.code}"

    @staticmethod
    def _extract_source(raw_result: dict[str, object], url: str) -> str:
        """Resolve a user-friendly source label from a Tavily result."""

        raw_source = raw_result.get("source")
        if isinstance(raw_source, str) and raw_source.strip():
            return raw_source.strip()

        hostname = urlparse(url).netloc.removeprefix("www.").strip()
        return hostname or "Unknown source"

    @staticmethod
    def _parse_published_at(value: object) -> datetime | None:
        """Parse Tavily's published date field into a timezone-aware timestamp."""

        if not isinstance(value, str) or not value.strip():
            return None

        normalized_value = value.strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized_value)
        except ValueError:
            try:
                return datetime.combine(date.fromisoformat(value[:10]), datetime.min.time())
            except ValueError:
                return None

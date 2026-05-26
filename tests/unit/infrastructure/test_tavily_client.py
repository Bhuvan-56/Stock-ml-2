"""Unit tests for the Tavily news provider."""

from __future__ import annotations

import json
from datetime import date

from pydantic import SecretStr

from stockml.core.config import NewsSettings
from stockml.domain.models import DailyNewsSearchRequest
from stockml.infrastructure.news.tavily_client import TavilyNewsProvider


class FakeResponse:
    """Simple context-manager response for urllib tests."""

    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:  # type: ignore[no-untyped-def]
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_tavily_provider_normalizes_articles(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    captured: dict[str, object] = {}

    def fake_urlopen(request, timeout):  # type: ignore[no-untyped-def]
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "results": [
                    {
                        "title": "Apple rallies on product reveal",
                        "url": "https://www.example.com/apple-rallies",
                        "content": "The company unveiled its newest hardware line.",
                        "published_date": "2024-01-05T14:30:00Z",
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "stockml.infrastructure.news.tavily_client.urlopen",
        fake_urlopen,
    )

    provider = TavilyNewsProvider(
        NewsSettings(
            enabled=True,
            tavily_api_key=SecretStr("test-key"),
            request_timeout_seconds=6,
            max_articles_per_anomaly=3,
        )
    )
    articles = provider.search_daily_news(
        DailyNewsSearchRequest(
            query="AAPL stock news 2024-01-05",
            trade_date=date(2024, 1, 5),
            max_results=2,
        )
    )

    assert captured["url"] == "https://api.tavily.com/search"
    assert captured["timeout"] == 6
    assert captured["body"] == {
        "api_key": "test-key",
        "query": "AAPL stock news 2024-01-05",
        "topic": "news",
        "max_results": 2,
        "start_date": "2024-01-05",
        "end_date": "2024-01-06",
    }
    assert len(articles) == 1
    assert articles[0].title == "Apple rallies on product reveal"
    assert articles[0].source == "example.com"
    assert articles[0].summary == "The company unveiled its newest hardware line."
    assert articles[0].published_at is not None

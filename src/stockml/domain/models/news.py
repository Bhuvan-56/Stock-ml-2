"""Typed domain models for contextual market news."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class DailyNewsSearchRequest:
    """Normalized request for exact-day market news lookups."""

    query: str
    trade_date: date
    max_results: int

    def __post_init__(self) -> None:
        normalized_query = self.query.strip()

        if not normalized_query:
            raise ValueError("News search query must not be blank.")
        if self.max_results <= 0:
            raise ValueError("max_results must be greater than zero.")

        object.__setattr__(self, "query", normalized_query)


@dataclass(frozen=True, slots=True)
class NewsArticle:
    """A normalized news article returned by an external search provider."""

    title: str
    url: str
    source: str
    summary: str | None = None
    published_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_title = self.title.strip()
        normalized_url = self.url.strip()
        normalized_source = self.source.strip()

        if not normalized_title:
            raise ValueError("News article title must not be blank.")
        if not normalized_url:
            raise ValueError("News article URL must not be blank.")
        if not normalized_source:
            raise ValueError("News article source must not be blank.")

        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "url", normalized_url)
        object.__setattr__(self, "source", normalized_source)
        if self.summary is not None:
            object.__setattr__(self, "summary", self.summary.strip() or None)

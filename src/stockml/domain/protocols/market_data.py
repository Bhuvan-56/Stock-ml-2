"""Protocols for market data integrations."""

from __future__ import annotations

from typing import Protocol

from stockml.domain.models import StockHistory, StockHistoryRequest


class StockDataProvider(Protocol):
    """Provide normalized historical stock prices from an upstream source."""

    def get_history(self, request: StockHistoryRequest) -> StockHistory:
        """Return normalized historical price records for the requested window."""

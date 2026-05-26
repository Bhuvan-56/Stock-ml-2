"""Unit tests for the stock data application service."""

from __future__ import annotations

from datetime import date

import pytest

from stockml.core.config import MarketDataSettings
from stockml.core.exceptions import InvalidRequestError
from stockml.domain.models import StockHistory, StockHistoryRequest, StockPriceRecord
from stockml.services.stock_data_service import StockDataService


class StubStockDataProvider:
    """Capture provider requests while returning a fixed history response."""

    def __init__(self, history: StockHistory) -> None:
        self.history = history
        self.last_request: StockHistoryRequest | None = None

    def get_history(self, request: StockHistoryRequest) -> StockHistory:
        self.last_request = request
        return self.history


def _build_history() -> StockHistory:
    return StockHistory(
        symbol="AAPL",
        interval="1d",
        records=(
            StockPriceRecord(
                trade_date=date(2024, 1, 2),
                open_price=100.0,
                high_price=103.0,
                low_price=99.0,
                close_price=102.0,
                volume=1_000_000,
                adjusted_close=101.5,
            ),
        ),
    )


def test_stock_data_service_normalizes_and_delegates_requests() -> None:
    provider = StubStockDataProvider(_build_history())
    service = StockDataService(provider=provider, settings=MarketDataSettings())

    history = service.get_history(
        symbol=" aapl ",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
    )

    assert history == provider.history
    assert provider.last_request == StockHistoryRequest(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31),
        interval="1d",
    )


def test_stock_data_service_rejects_invalid_date_ranges() -> None:
    service = StockDataService(
        provider=StubStockDataProvider(_build_history()),
        settings=MarketDataSettings(),
    )

    with pytest.raises(InvalidRequestError):
        service.get_history(
            symbol="AAPL",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 1, 31),
        )


def test_stock_data_service_builds_default_history_window() -> None:
    provider = StubStockDataProvider(_build_history())
    service = StockDataService(
        provider=provider,
        settings=MarketDataSettings(default_history_years=3),
    )

    service.get_default_history(symbol="msft", as_of=date(2026, 5, 25))

    assert provider.last_request == StockHistoryRequest(
        symbol="MSFT",
        start_date=date(2023, 5, 25),
        end_date=date(2026, 5, 25),
        interval="1d",
    )

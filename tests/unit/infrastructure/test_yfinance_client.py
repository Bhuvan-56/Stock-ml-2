"""Unit tests for the yfinance market data provider."""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest
from yfinance import exceptions as yf_exceptions

from stockml.core.config import MarketDataSettings
from stockml.core.exceptions import ResourceNotFoundError, UpstreamServiceError
from stockml.domain.models import StockHistoryRequest
from stockml.infrastructure.market_data.yfinance_client import YFinanceStockDataProvider


def test_yfinance_provider_normalizes_downloaded_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_kwargs: dict[str, object] = {}

    class FakeTicker:
        def history(self, **kwargs: object) -> pd.DataFrame:
            captured_kwargs.update(kwargs)
            return pd.DataFrame(
                {
                    "Open": [100.0, 101.0],
                    "High": [102.0, 103.0],
                    "Low": [99.0, 100.0],
                    "Close": [101.5, 102.5],
                    "Adj Close": [101.2, 102.1],
                    "Volume": [1_000_000, 1_200_000],
                },
                index=pd.date_range("2024-01-02", periods=2, freq="D"),
            )

    monkeypatch.setattr(
        "stockml.infrastructure.market_data.yfinance_client.yf.Ticker",
        lambda symbol: FakeTicker(),
    )

    provider = YFinanceStockDataProvider(settings=MarketDataSettings())
    history = provider.get_history(
        StockHistoryRequest(
            symbol="aapl",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 3),
        )
    )

    assert captured_kwargs == {
        "start": "2024-01-01",
        "end": "2024-01-04",
        "interval": "1d",
        "auto_adjust": False,
        "actions": False,
        "timeout": 30,
    }
    assert history.symbol == "AAPL"
    assert history.start_date == date(2024, 1, 2)
    assert history.end_date == date(2024, 1, 3)
    assert history.row_count == 2
    assert history.records[0].adjusted_close == 101.2

    frame = history.to_dataframe()
    assert tuple(frame.columns) == (
        "open",
        "high",
        "low",
        "close",
        "volume",
        "adjusted_close",
    )
    assert frame.loc[date(2024, 1, 3), "close"] == 102.5


def test_yfinance_provider_handles_multiindex_columns(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    columns = pd.MultiIndex.from_product(
        [["Open", "High", "Low", "Close", "Volume"], ["AAPL"]],
    )
    frame = pd.DataFrame(
        [[100.0, 103.0, 99.0, 102.0, 1_000_000]],
        columns=columns,
        index=pd.date_range("2024-01-02", periods=1, freq="D"),
    )

    class FakeTicker:
        def history(self, **_: object) -> pd.DataFrame:
            return frame

    monkeypatch.setattr(
        "stockml.infrastructure.market_data.yfinance_client.yf.Ticker",
        lambda symbol: FakeTicker(),
    )

    provider = YFinanceStockDataProvider(settings=MarketDataSettings())
    history = provider.get_history(
        StockHistoryRequest(
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
        )
    )

    assert history.row_count == 1
    assert history.records[0].close_price == 102.0


def test_yfinance_provider_raises_when_no_rows_are_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTicker:
        def history(self, **_: object) -> pd.DataFrame:
            return pd.DataFrame()

    monkeypatch.setattr(
        "stockml.infrastructure.market_data.yfinance_client.yf.Ticker",
        lambda symbol: FakeTicker(),
    )

    provider = YFinanceStockDataProvider(settings=MarketDataSettings())

    with pytest.raises(ResourceNotFoundError):
        provider.get_history(
            StockHistoryRequest(
                symbol="AAPL",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 2),
            )
        )


def test_yfinance_provider_translates_timeout_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTicker:
        def history(self, **_: object) -> pd.DataFrame:
            raise TimeoutError("curl: (28) Connection timed out")

    monkeypatch.setattr(
        "stockml.infrastructure.market_data.yfinance_client.yf.Ticker",
        lambda symbol: FakeTicker(),
    )

    provider = YFinanceStockDataProvider(settings=MarketDataSettings())

    with pytest.raises(UpstreamServiceError, match="timed out while loading symbol 'AAPL'"):
        provider.get_history(
            StockHistoryRequest(
                symbol="AAPL",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 2),
            )
        )


def test_yfinance_provider_translates_missing_ticker_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeTicker:
        def history(self, **_: object) -> pd.DataFrame:
            raise yf_exceptions.YFTzMissingError("AAPL")

    monkeypatch.setattr(
        "stockml.infrastructure.market_data.yfinance_client.yf.Ticker",
        lambda symbol: FakeTicker(),
    )

    provider = YFinanceStockDataProvider(settings=MarketDataSettings())

    with pytest.raises(ResourceNotFoundError):
        provider.get_history(
            StockHistoryRequest(
                symbol="AAPL",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 2),
            )
        )

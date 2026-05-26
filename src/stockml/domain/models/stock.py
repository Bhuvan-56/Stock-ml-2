"""Typed domain models for normalized stock market history."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd


@dataclass(frozen=True, slots=True)
class StockHistoryRequest:
    """Normalized request object for historical market data."""

    symbol: str
    start_date: date
    end_date: date
    interval: str = "1d"

    def __post_init__(self) -> None:
        normalized_symbol = self.symbol.strip().upper()
        normalized_interval = self.interval.strip().lower()

        if not normalized_symbol:
            raise ValueError("Stock symbol must not be blank.")
        if self.start_date > self.end_date:
            raise ValueError("start_date must be less than or equal to end_date.")
        if normalized_interval != "1d":
            raise ValueError("Only the '1d' interval is currently supported.")

        object.__setattr__(self, "symbol", normalized_symbol)
        object.__setattr__(self, "interval", normalized_interval)

    @property
    def provider_end_date_exclusive(self) -> date:
        """Return the exclusive end date expected by upstream providers."""

        return self.end_date + timedelta(days=1)


@dataclass(frozen=True, slots=True)
class StockPriceRecord:
    """A normalized daily OHLCV record."""

    trade_date: date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    adjusted_close: float | None = None

    def __post_init__(self) -> None:
        if self.high_price < self.low_price:
            raise ValueError("high_price must be greater than or equal to low_price.")
        if self.volume < 0:
            raise ValueError("volume must be non-negative.")


@dataclass(frozen=True, slots=True)
class StockHistory:
    """Chronological normalized price history for a stock symbol."""

    symbol: str
    interval: str
    records: tuple[StockPriceRecord, ...]
    source: str = "yfinance"

    def __post_init__(self) -> None:
        normalized_symbol = self.symbol.strip().upper()
        normalized_interval = self.interval.strip().lower()

        if not normalized_symbol:
            raise ValueError("Stock history symbol must not be blank.")
        if not self.records:
            raise ValueError("Stock history must contain at least one record.")
        if normalized_interval != "1d":
            raise ValueError("Only the '1d' interval is currently supported.")

        previous_date: date | None = None
        seen_dates: set[date] = set()
        for record in self.records:
            if previous_date is not None and record.trade_date < previous_date:
                raise ValueError("Stock history records must be chronological.")
            if record.trade_date in seen_dates:
                raise ValueError("Stock history records must not contain duplicate dates.")
            seen_dates.add(record.trade_date)
            previous_date = record.trade_date

        object.__setattr__(self, "symbol", normalized_symbol)
        object.__setattr__(self, "interval", normalized_interval)

    @property
    def start_date(self) -> date:
        """Return the first available trade date."""

        return self.records[0].trade_date

    @property
    def end_date(self) -> date:
        """Return the last available trade date."""

        return self.records[-1].trade_date

    @property
    def row_count(self) -> int:
        """Return the number of normalized records."""

        return len(self.records)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert normalized records into a pandas DataFrame for the ML layer."""

        frame = pd.DataFrame(
            {
                "open": [record.open_price for record in self.records],
                "high": [record.high_price for record in self.records],
                "low": [record.low_price for record in self.records],
                "close": [record.close_price for record in self.records],
                "volume": [record.volume for record in self.records],
                "adjusted_close": [record.adjusted_close for record in self.records],
            },
            index=pd.Index([record.trade_date for record in self.records], name="date"),
        )
        return frame

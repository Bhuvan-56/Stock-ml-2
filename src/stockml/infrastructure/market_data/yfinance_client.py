"""yfinance-backed market data provider."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import yfinance as yf
from yfinance import exceptions as yf_exceptions

from stockml.core.config import MarketDataSettings
from stockml.core.exceptions import ResourceNotFoundError, UpstreamServiceError
from stockml.domain.models import StockHistory, StockHistoryRequest, StockPriceRecord


class YFinanceStockDataProvider:
    """Retrieve and normalize daily stock history through yfinance."""

    def __init__(self, settings: MarketDataSettings) -> None:
        self._settings = settings
        self._configure_cache_directory(settings.cache_directory)
        self._configure_runtime()

    def get_history(self, request: StockHistoryRequest) -> StockHistory:
        """Download and normalize historical prices for a stock symbol."""

        try:
            frame = self._fetch_history_frame(request)
        except yf_exceptions.YFTickerMissingError as exc:
            raise ResourceNotFoundError(
                f"No historical price data was returned for symbol '{request.symbol}'."
            ) from exc
        except yf_exceptions.YFRateLimitError as exc:
            raise UpstreamServiceError(
                "Yahoo Finance rate limited the market-data request. Try again shortly."
            ) from exc
        except TimeoutError as exc:
            raise UpstreamServiceError(
                f"Yahoo Finance timed out while loading symbol '{request.symbol}'."
            ) from exc
        except Exception as exc:  # pragma: no cover - defensive boundary
            if self._is_timeout_error(exc):
                raise UpstreamServiceError(
                    f"Yahoo Finance timed out while loading symbol '{request.symbol}'."
                ) from exc

            raise UpstreamServiceError(
                f"Failed to download market data for symbol '{request.symbol}' from Yahoo Finance."
            ) from exc

        normalized_frame = self._normalize_frame(frame, request.symbol)
        records = self._build_records(normalized_frame)
        return StockHistory(
            symbol=request.symbol,
            interval=request.interval,
            records=records,
            source="yfinance",
        )

    @staticmethod
    def _configure_cache_directory(cache_directory: str) -> None:
        """Move yfinance caches into an application-controlled writable directory."""

        resolved_cache_directory = Path(cache_directory).expanduser().resolve()
        resolved_cache_directory.mkdir(parents=True, exist_ok=True)
        yf.set_tz_cache_location(str(resolved_cache_directory))

    def _configure_runtime(self) -> None:
        """Configure yfinance runtime behavior for clearer application errors."""

        yf.config.debug.hide_exceptions = False
        yf.config.network.retries = self._settings.request_retries

    def _fetch_history_frame(self, request: StockHistoryRequest) -> pd.DataFrame:
        """Fetch single-ticker history with explicit exception propagation."""

        ticker = yf.Ticker(request.symbol)
        return ticker.history(
            start=request.start_date.isoformat(),
            end=request.provider_end_date_exclusive.isoformat(),
            interval=request.interval,
            auto_adjust=False,
            actions=False,
            timeout=self._settings.request_timeout_seconds,
        )

    def _normalize_frame(self, frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Normalize yfinance output into a predictable OHLCV frame."""

        if frame.empty:
            raise ResourceNotFoundError(
                f"No historical price data was returned for symbol '{symbol}'."
            )

        normalized = frame.copy()
        if isinstance(normalized.columns, pd.MultiIndex):
            normalized.columns = normalized.columns.get_level_values(0)

        required_columns = ["Open", "High", "Low", "Close", "Volume"]
        optional_columns = ["Adj Close"]
        missing_columns = [column for column in required_columns if column not in normalized.columns]
        if missing_columns:
            raise UpstreamServiceError(
                "yfinance response is missing required OHLCV columns."
            )

        selected_columns = required_columns + [
            column for column in optional_columns if column in normalized.columns
        ]
        normalized = normalized.loc[:, selected_columns].copy()
        normalized = normalized.sort_index()
        normalized = normalized.loc[~normalized.index.duplicated(keep="last")]
        normalized = normalized.dropna(subset=required_columns)

        if isinstance(normalized.index, pd.DatetimeIndex) and normalized.index.tz is not None:
            normalized.index = normalized.index.tz_localize(None)

        if normalized.empty:
            raise ResourceNotFoundError(
                f"No usable historical price data was returned for symbol '{symbol}'."
            )

        return normalized

    @staticmethod
    def _build_records(frame: pd.DataFrame) -> tuple[StockPriceRecord, ...]:
        """Convert a normalized OHLCV frame into typed records."""

        records: list[StockPriceRecord] = []
        for row_label, row in frame.iterrows():
            records.append(
                StockPriceRecord(
                    trade_date=YFinanceStockDataProvider._coerce_trade_date(row_label),
                    open_price=float(row["Open"]),
                    high_price=float(row["High"]),
                    low_price=float(row["Low"]),
                    close_price=float(row["Close"]),
                    volume=int(float(row["Volume"])),
                    adjusted_close=(
                        None
                        if "Adj Close" not in frame.columns or pd.isna(row["Adj Close"])
                        else float(row["Adj Close"])
                    ),
                )
            )
        return tuple(records)

    @staticmethod
    def _coerce_trade_date(value: object) -> date:
        """Convert pandas index labels into plain trade dates."""

        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        raise UpstreamServiceError("yfinance returned an unsupported index type.")

    @staticmethod
    def _is_timeout_error(exc: Exception) -> bool:
        """Return whether the upstream exception looks like a timeout."""

        normalized_message = str(exc).lower()
        return "timed out" in normalized_message or "curl: (28)" in normalized_message

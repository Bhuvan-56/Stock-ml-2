"""Feature engineering for stock price prediction."""

from __future__ import annotations

from typing import Final

import pandas as pd

from stockml.core.exceptions import TrainingDataError
from stockml.domain.models import FeatureSet

DEFAULT_MOVING_AVERAGE_WINDOWS: Final[tuple[int, ...]] = (7, 14, 21)
DEFAULT_VOLATILITY_WINDOW: Final[int] = 7
DEFAULT_TARGET_COLUMN: Final[str] = "close"


class RollingWindowFeatureEngineer:
    """Build rolling-window technical features from normalized OHLCV history."""

    def __init__(
        self,
        *,
        moving_average_windows: tuple[int, ...] = DEFAULT_MOVING_AVERAGE_WINDOWS,
        volatility_window: int = DEFAULT_VOLATILITY_WINDOW,
        target_column: str = DEFAULT_TARGET_COLUMN,
    ) -> None:
        if not moving_average_windows:
            raise ValueError("At least one moving-average window must be configured.")
        if any(window <= 0 for window in moving_average_windows):
            raise ValueError("Moving-average windows must be positive integers.")
        if len(set(moving_average_windows)) != len(moving_average_windows):
            raise ValueError("Moving-average windows must be unique.")
        if volatility_window <= 0:
            raise ValueError("volatility_window must be a positive integer.")
        if not target_column.strip():
            raise ValueError("target_column must not be blank.")

        self._moving_average_windows = moving_average_windows
        self._volatility_window = volatility_window
        self._target_column = target_column.strip().lower()

    def build_feature_set(self, market_history: pd.DataFrame) -> FeatureSet:
        """Transform normalized price history into model-ready rolling features."""

        normalized_history = self._normalize_market_history(market_history)
        feature_frame = pd.DataFrame(index=normalized_history.index)
        feature_frame["high_low_spread"] = normalized_history["high"] - normalized_history["low"]
        feature_frame["open_close_spread"] = normalized_history["open"] - normalized_history["close"]

        for window in self._moving_average_windows:
            feature_frame[f"close_ma_{window}"] = normalized_history["close"].rolling(window).mean()

        feature_frame[f"close_std_{self._volatility_window}"] = (
            normalized_history["close"].rolling(self._volatility_window).std()
        )
        feature_frame["volume"] = normalized_history["volume"]

        target_series = normalized_history[self._target_column].rename(self._target_column)
        combined = pd.concat([feature_frame, target_series], axis=1).dropna()

        if combined.empty:
            raise TrainingDataError(
                "Market history does not contain enough rows after feature engineering."
            )

        feature_columns = tuple(
            column for column in combined.columns if column != self._target_column
        )

        return FeatureSet(
            feature_frame=combined.loc[:, feature_columns].copy(),
            target_series=combined.loc[:, self._target_column].copy(),
            feature_columns=feature_columns,
            target_column=self._target_column,
        )

    def _normalize_market_history(self, market_history: pd.DataFrame) -> pd.DataFrame:
        """Validate and normalize input history into lowercase OHLCV columns."""

        if market_history.empty:
            raise TrainingDataError("Market history must contain at least one row.")
        if market_history.index.has_duplicates:
            raise TrainingDataError("Market history must not contain duplicate index labels.")
        if not market_history.index.is_monotonic_increasing:
            raise TrainingDataError("Market history must be sorted chronologically.")

        normalized_history = market_history.copy()
        normalized_history.columns = [str(column).strip().lower() for column in market_history.columns]

        required_columns = {"open", "high", "low", "close", "volume", self._target_column}
        missing_columns = required_columns.difference(normalized_history.columns)
        if missing_columns:
            missing_column_list = ", ".join(sorted(missing_columns))
            raise TrainingDataError(
                f"Market history is missing required columns: {missing_column_list}."
            )

        return normalized_history

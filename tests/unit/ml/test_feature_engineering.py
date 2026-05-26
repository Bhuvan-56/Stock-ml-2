"""Unit tests for rolling-window feature engineering."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from stockml.core.exceptions import TrainingDataError
from stockml.ml.feature_engineering import RollingWindowFeatureEngineer


def _build_market_history(row_count: int = 30) -> pd.DataFrame:
    index = pd.date_range("2024-01-01", periods=row_count, freq="D")
    open_prices = [100.0 + float(value) for value in range(row_count)]
    close_prices = [price + 1.0 for price in open_prices]

    return pd.DataFrame(
        {
            "open": open_prices,
            "high": [price + 2.0 for price in open_prices],
            "low": [price - 1.0 for price in open_prices],
            "close": close_prices,
            "volume": [1_000_000 + value * 1000 for value in range(row_count)],
        },
        index=index,
    )


def test_rolling_window_feature_engineer_builds_expected_feature_set() -> None:
    engineer = RollingWindowFeatureEngineer()
    market_history = _build_market_history()

    feature_set = engineer.build_feature_set(market_history)

    assert feature_set.feature_columns == (
        "high_low_spread",
        "open_close_spread",
        "close_ma_7",
        "close_ma_14",
        "close_ma_21",
        "close_std_7",
        "volume",
    )
    assert feature_set.target_column == "close"
    assert feature_set.row_count == 10
    assert feature_set.feature_frame.index[0] == pd.Timestamp("2024-01-21")
    assert feature_set.target_series.iloc[0] == 121.0

    first_row = feature_set.feature_frame.iloc[0]
    expected_close_window = market_history.loc["2024-01-15":"2024-01-21", "close"]

    assert first_row["high_low_spread"] == 3.0
    assert first_row["open_close_spread"] == -1.0
    assert first_row["close_ma_7"] == expected_close_window.mean()
    assert first_row["close_ma_14"] == market_history.loc["2024-01-08":"2024-01-21", "close"].mean()
    assert first_row["close_ma_21"] == market_history.loc["2024-01-01":"2024-01-21", "close"].mean()
    assert math.isclose(
        first_row["close_std_7"],
        expected_close_window.std(),
        rel_tol=1e-9,
    )
    assert first_row["volume"] == 1_020_000


def test_rolling_window_feature_engineer_rejects_missing_columns() -> None:
    engineer = RollingWindowFeatureEngineer()
    market_history = _build_market_history().drop(columns=["volume"])

    with pytest.raises(TrainingDataError):
        engineer.build_feature_set(market_history)


def test_rolling_window_feature_engineer_rejects_insufficient_rows() -> None:
    engineer = RollingWindowFeatureEngineer()
    market_history = _build_market_history(row_count=10)

    with pytest.raises(TrainingDataError):
        engineer.build_feature_set(market_history)

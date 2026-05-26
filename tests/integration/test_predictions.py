"""Integration tests for the prediction endpoint."""

from __future__ import annotations

import math
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.api.dependencies import get_stock_data_provider
from stockml.core.config import ModelSettings, Settings
from stockml.domain.models import StockHistory, StockHistoryRequest, StockPriceRecord
from stockml.main import create_app


class StubStockDataProvider:
    """Return fixed history while capturing normalized provider requests."""

    def __init__(self, history: StockHistory) -> None:
        self.history = history
        self.requests: list[StockHistoryRequest] = []

    def get_history(self, request: StockHistoryRequest) -> StockHistory:
        self.requests.append(request)
        return self.history


def _build_history(symbol: str = "AAPL", row_count: int = 160) -> StockHistory:
    start_date = date(2024, 1, 1)
    records: list[StockPriceRecord] = []

    for offset in range(row_count):
        trade_date = start_date + timedelta(days=offset)
        base_price = 100.0 + offset * 0.45
        close_price = base_price + math.sin(offset / 8.0)
        records.append(
            StockPriceRecord(
                trade_date=trade_date,
                open_price=base_price - 0.3,
                high_price=base_price + 1.4,
                low_price=base_price - 1.1,
                close_price=close_price,
                volume=1_000_000 + offset * 1_500,
                adjusted_close=close_price - 0.15,
            )
        )

    return StockHistory(symbol=symbol, interval="1d", records=tuple(records))


def _create_test_app(provider: StubStockDataProvider):
    app = create_app(
        Settings(
            _env_file=None,
            environment="test",
            model=ModelSettings(
                training_split_ratio=0.8,
                minimum_training_rows=40,
                hidden_units=8,
                epochs=150,
                batch_size=16,
                random_seed=7,
            ),
        )
    )
    app.dependency_overrides[get_stock_data_provider] = lambda: provider
    return app


def test_prediction_endpoint_returns_structured_payload() -> None:
    provider = StubStockDataProvider(_build_history())
    app = _create_test_app(provider)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/predictions/",
            json={
                "symbol": " aapl ",
                "start_date": "2024-01-01",
                "end_date": "2024-06-08",
            },
        )

    assert response.status_code == 200
    assert len(provider.requests) == 1
    assert provider.requests[0] == StockHistoryRequest(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 8),
        interval="1d",
    )

    payload = response.json()
    assert payload["symbol"] == "AAPL"
    assert payload["stock_window"] == {
        "requested_start_date": "2024-01-01",
        "requested_end_date": "2024-06-08",
        "actual_start_date": "2024-01-01",
        "actual_end_date": "2024-06-08",
        "interval": "1d",
        "row_count": 160,
    }
    assert payload["feature_columns"] == [
        "high_low_spread",
        "open_close_spread",
        "close_ma_7",
        "close_ma_14",
        "close_ma_21",
        "close_std_7",
        "volume",
    ]
    assert payload["metrics"]["training_rows"] == 112
    assert payload["metrics"]["validation_rows"] == 28
    assert payload["metrics"]["feature_count"] == 7
    assert payload["metadata"]["model_name"] == "mlp_regressor"
    assert payload["metadata"]["source"] == "yfinance"
    assert payload["metadata"]["cached"] is False
    assert payload["metadata"]["prediction_count"] == 28
    assert payload["metadata"]["news_status"] == "disabled"
    assert payload["metadata"]["news_provider"] is None
    assert payload["metadata"]["anomaly_count"] == len(payload["anomalies"])
    assert len(payload["price_history"]) == 160
    assert len(payload["predictions"]) == 28
    assert payload["predictions"][0]["date"] == "2024-05-12"


def test_prediction_endpoint_reuses_cached_response_for_identical_requests() -> None:
    provider = StubStockDataProvider(_build_history())
    app = _create_test_app(provider)

    request_payload = {
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-06-08",
    }

    with TestClient(app) as client:
        first_response = client.post("/api/v1/predictions/", json=request_payload)
        second_response = client.post("/api/v1/predictions/", json=request_payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert len(provider.requests) == 1
    assert first_response.json()["metadata"]["cached"] is False
    assert second_response.json()["metadata"]["cached"] is True


def test_prediction_endpoint_rejects_inverted_date_windows() -> None:
    provider = StubStockDataProvider(_build_history())
    app = _create_test_app(provider)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/predictions/",
            json={
                "symbol": "AAPL",
                "start_date": "2024-07-01",
                "end_date": "2024-06-01",
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_error"
    assert len(provider.requests) == 0

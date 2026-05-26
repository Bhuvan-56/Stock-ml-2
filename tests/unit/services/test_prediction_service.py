"""Unit tests for prediction service anomaly enrichment."""

from __future__ import annotations

from datetime import date, datetime, timezone

from pydantic import SecretStr

from stockml.core.config import MarketDataSettings, NewsSettings
from stockml.domain.models import (
    ModelTrainingResult,
    NewsArticle,
    PredictionPoint,
    StockHistory,
    StockHistoryRequest,
    StockPriceRecord,
    TrainingMetrics,
)
from stockml.services.news_service import NewsService
from stockml.services.prediction_service import PredictionResultCache, PredictionService
from stockml.services.stock_data_service import StockDataService
from stockml.schemas.prediction import PredictionRequest


class StubStockDataProvider:
    """Return fixed stock history for prediction service tests."""

    def __init__(self, history: StockHistory) -> None:
        self.history = history
        self.requests: list[StockHistoryRequest] = []

    def get_history(self, request: StockHistoryRequest) -> StockHistory:
        self.requests.append(request)
        return self.history


class StubPredictionPipeline:
    """Return a predetermined training result."""

    def __init__(self, result: ModelTrainingResult) -> None:
        self.result = result
        self.calls = 0

    def run(self, market_history):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self.result


class StubNewsProvider:
    """Return predefined news grouped by anomaly date."""

    provider_name = "tavily"

    def __init__(self, articles_by_date: dict[date, tuple[NewsArticle, ...]]) -> None:
        self.articles_by_date = articles_by_date
        self.requests = []

    def search_daily_news(self, request):  # type: ignore[no-untyped-def]
        self.requests.append(request)
        return self.articles_by_date.get(request.trade_date, ())


def _build_history() -> StockHistory:
    return StockHistory(
        symbol="AAPL",
        interval="1d",
        records=(
            StockPriceRecord(
                trade_date=date(2024, 1, 2),
                open_price=100.0,
                high_price=102.0,
                low_price=99.0,
                close_price=101.0,
                volume=1_000_000,
            ),
            StockPriceRecord(
                trade_date=date(2024, 1, 3),
                open_price=101.0,
                high_price=104.0,
                low_price=100.0,
                close_price=103.0,
                volume=1_100_000,
            ),
            StockPriceRecord(
                trade_date=date(2024, 1, 4),
                open_price=103.0,
                high_price=106.0,
                low_price=102.0,
                close_price=104.0,
                volume=1_120_000,
            ),
            StockPriceRecord(
                trade_date=date(2024, 1, 5),
                open_price=104.0,
                high_price=132.0,
                low_price=103.0,
                close_price=130.0,
                volume=1_450_000,
            ),
        ),
    )


def _build_training_result() -> ModelTrainingResult:
    return ModelTrainingResult(
        model_name="stub_model",
        target_column="close",
        feature_columns=("momentum", "volume"),
        metrics=TrainingMetrics(
            mae=5.0,
            rmse=3.0,
            training_rows=80,
            validation_rows=3,
            feature_count=2,
        ),
        predictions=(
            PredictionPoint(row_label="2024-01-03", actual=103.0, predicted=95.0),
            PredictionPoint(row_label="2024-01-04", actual=104.0, predicted=103.0),
            PredictionPoint(row_label="2024-01-05", actual=130.0, predicted=118.0),
        ),
    )


def test_prediction_service_enriches_large_anomalies_with_news() -> None:
    history = _build_history()
    stock_data_provider = StubStockDataProvider(history)
    stock_data_service = StockDataService(
        provider=stock_data_provider,
        settings=MarketDataSettings(),
    )
    prediction_pipeline = StubPredictionPipeline(_build_training_result())
    news_provider = StubNewsProvider(
        {
            date(2024, 1, 5): (
                NewsArticle(
                    title="Apple jumps after product announcement",
                    url="https://example.com/apple-jumps",
                    source="example.com",
                    summary="Investors reacted to a major product update.",
                    published_at=datetime(2024, 1, 5, 14, 30, tzinfo=timezone.utc),
                ),
            ),
        }
    )
    news_service = NewsService(
        settings=NewsSettings(
            enabled=True,
            tavily_api_key=SecretStr("test-key"),
            max_anomaly_days=2,
            max_articles_per_anomaly=3,
        ),
        provider=news_provider,
    )
    service = PredictionService(
        stock_data_service=stock_data_service,
        prediction_pipeline=prediction_pipeline,
        market_data_settings=MarketDataSettings(default_history_years=3),
        news_service=news_service,
        cache=PredictionResultCache(),
        generated_at_factory=lambda: datetime(2024, 1, 6, tzinfo=timezone.utc),
    )

    response = service.predict(
        PredictionRequest(
            symbol="AAPL",
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 5),
        )
    )

    assert prediction_pipeline.calls == 1
    assert len(stock_data_provider.requests) == 1
    assert response.metadata.news_status == "ready"
    assert response.metadata.news_provider == "tavily"
    assert response.metadata.anomaly_count == 2
    assert len(response.anomalies) == 2
    assert response.anomalies[0].date == date(2024, 1, 5)
    assert response.anomalies[0].absolute_residual == 12.0
    assert response.anomalies[0].news[0].title == "Apple jumps after product announcement"
    assert response.anomalies[1].date == date(2024, 1, 3)
    assert response.anomalies[1].news == []


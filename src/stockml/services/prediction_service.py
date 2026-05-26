"""Application service for stock prediction requests."""

from __future__ import annotations

import logging
from collections import OrderedDict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from threading import Lock
from typing import Callable, Literal

from stockml.core.config import MarketDataSettings
from stockml.core.exceptions import InvalidRequestError, UpstreamServiceError
from stockml.domain.models import ModelTrainingResult, NewsArticle, PredictionPoint, StockHistory
from stockml.ml.pipeline import PredictionPipeline
from stockml.schemas.prediction import (
    HistoricalPricePointResponse,
    NewsArticleResponse,
    PredictionAnomalyResponse,
    PredictionMetadataResponse,
    PredictionMetricsResponse,
    PredictionPointResponse,
    PredictionRequest,
    PredictionResponse,
    PredictionStockWindow,
)
from stockml.services.news_service import NewsService
from stockml.services.stock_data_service import StockDataService

logger = logging.getLogger("stockml.services.prediction_service")
NewsStatus = Literal["disabled", "ready", "unavailable"]


@dataclass(frozen=True, slots=True)
class PredictionCacheKey:
    """Cache key for a normalized prediction request."""

    symbol: str
    start_date: date
    end_date: date


@dataclass(frozen=True, slots=True)
class ResolvedPredictionWindow:
    """Resolved explicit date window used for market-data retrieval."""

    start_date: date
    end_date: date


@dataclass(frozen=True, slots=True)
class ResolvedPredictionAnomaly:
    """A validation point with a large absolute residual and a parseable date."""

    date: date
    actual: float
    predicted: float
    residual: float
    absolute_residual: float
    anomaly_threshold: float


class PredictionResultCache:
    """Small thread-safe in-memory cache for deterministic prediction responses."""

    def __init__(self, max_entries: int = 128) -> None:
        if max_entries <= 0:
            raise ValueError("max_entries must be greater than zero.")

        self._max_entries = max_entries
        self._entries: OrderedDict[PredictionCacheKey, PredictionResponse] = OrderedDict()
        self._lock = Lock()

    def get(self, key: PredictionCacheKey) -> PredictionResponse | None:
        """Return a cached response copy if the normalized request is present."""

        with self._lock:
            cached_response = self._entries.get(key)
            if cached_response is None:
                return None
            self._entries.move_to_end(key)
            return cached_response.model_copy(deep=True)

    def set(self, key: PredictionCacheKey, response: PredictionResponse) -> None:
        """Store a deep copy of the response and evict the oldest entry if needed."""

        with self._lock:
            self._entries[key] = response.model_copy(deep=True)
            self._entries.move_to_end(key)
            if len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)


class PredictionService:
    """Generate structured stock predictions for the HTTP API."""

    def __init__(
        self,
        *,
        stock_data_service: StockDataService,
        prediction_pipeline: PredictionPipeline,
        market_data_settings: MarketDataSettings,
        news_service: NewsService,
        cache: PredictionResultCache,
        today_factory: Callable[[], date] | None = None,
        generated_at_factory: Callable[[], datetime] | None = None,
    ) -> None:
        self._stock_data_service = stock_data_service
        self._prediction_pipeline = prediction_pipeline
        self._market_data_settings = market_data_settings
        self._news_service = news_service
        self._cache = cache
        self._today_factory = today_factory or date.today
        self._generated_at_factory = generated_at_factory or self._default_generated_at

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Fetch market data, run the pipeline, and return a typed API payload."""

        window = self._resolve_window(request)
        cache_key = PredictionCacheKey(
            symbol=request.symbol,
            start_date=window.start_date,
            end_date=window.end_date,
        )

        cached_response = self._cache.get(cache_key)
        if cached_response is not None:
            return self._mark_cached(cached_response)

        market_history = self._stock_data_service.get_history(
            symbol=request.symbol,
            start_date=window.start_date,
            end_date=window.end_date,
        )
        training_result = self._prediction_pipeline.run(market_history.to_dataframe())
        anomalies, news_status = self._build_anomalies(
            symbol=request.symbol,
            training_result=training_result,
        )
        response = self._build_response(
            history=market_history,
            training_result=training_result,
            window=window,
            anomalies=anomalies,
            news_status=news_status,
        )
        self._cache.set(cache_key, response)
        return response

    def _resolve_window(self, request: PredictionRequest) -> ResolvedPredictionWindow:
        """Resolve omitted dates into an explicit market-data window."""

        resolved_end_date = request.end_date or self._today_factory()
        resolved_start_date = request.start_date or self._subtract_years(
            resolved_end_date,
            self._market_data_settings.default_history_years,
        )

        if resolved_start_date > resolved_end_date:
            raise InvalidRequestError("start_date must be less than or equal to end_date.")

        return ResolvedPredictionWindow(
            start_date=resolved_start_date,
            end_date=resolved_end_date,
        )

    def _build_response(
        self,
        *,
        history: StockHistory,
        training_result: ModelTrainingResult,
        window: ResolvedPredictionWindow,
        anomalies: tuple[PredictionAnomalyResponse, ...],
        news_status: NewsStatus,
    ) -> PredictionResponse:
        """Transform domain models into the frontend-facing response contract."""

        return PredictionResponse(
            symbol=history.symbol,
            stock_window=PredictionStockWindow(
                requested_start_date=window.start_date,
                requested_end_date=window.end_date,
                actual_start_date=history.start_date,
                actual_end_date=history.end_date,
                interval=history.interval,
                row_count=history.row_count,
            ),
            feature_columns=list(training_result.feature_columns),
            metrics=PredictionMetricsResponse(
                mae=training_result.metrics.mae,
                rmse=training_result.metrics.rmse,
                training_rows=training_result.metrics.training_rows,
                validation_rows=training_result.metrics.validation_rows,
                feature_count=training_result.metrics.feature_count,
            ),
            price_history=[
                HistoricalPricePointResponse(
                    date=record.trade_date,
                    open=record.open_price,
                    high=record.high_price,
                    low=record.low_price,
                    close=record.close_price,
                    volume=record.volume,
                )
                for record in history.records
            ],
            predictions=[
                PredictionPointResponse(
                    label=prediction.row_label,
                    date=self._parse_prediction_date(prediction.row_label),
                    actual=prediction.actual,
                    predicted=prediction.predicted,
                    residual=prediction.actual - prediction.predicted,
                )
                for prediction in training_result.predictions
            ],
            anomalies=list(anomalies),
            metadata=PredictionMetadataResponse(
                model_name=training_result.model_name,
                target_column=training_result.target_column,
                source=history.source,
                generated_at=self._generated_at_factory(),
                cached=False,
                prediction_count=len(training_result.predictions),
                anomaly_count=len(anomalies),
                news_status=news_status,
                news_provider=self._news_service.provider_name,
            ),
        )

    def _build_anomalies(
        self,
        *,
        symbol: str,
        training_result: ModelTrainingResult,
    ) -> tuple[tuple[PredictionAnomalyResponse, ...], NewsStatus]:
        """Build large-error anomaly entries and enrich them with same-day news."""

        selected_anomalies = self._select_anomalies(
            predictions=training_result.predictions,
            rmse=training_result.metrics.rmse,
        )

        if not selected_anomalies:
            return (), "disabled" if not self._news_service.is_enabled else "ready"

        if not self._news_service.is_enabled:
            return (
                tuple(
                    self._serialize_anomaly(anomaly=anomaly, news_articles=())
                    for anomaly in selected_anomalies
                ),
                "disabled",
            )

        try:
            return (
                tuple(
                    self._serialize_anomaly(
                        anomaly=anomaly,
                        news_articles=self._news_service.search_market_news(
                            symbol=symbol,
                            trade_date=anomaly.date,
                        ),
                    )
                    for anomaly in selected_anomalies
                ),
                "ready",
            )
        except UpstreamServiceError as exc:
            logger.warning(
                "Failed to retrieve anomaly news context for %s.",
                symbol,
                exc_info=exc,
            )
            return (
                tuple(
                    self._serialize_anomaly(anomaly=anomaly, news_articles=())
                    for anomaly in selected_anomalies
                ),
                "unavailable",
            )

    @staticmethod
    def _mark_cached(response: PredictionResponse) -> PredictionResponse:
        """Return a copy of a response flagged as cache-derived."""

        return response.model_copy(
            update={
                "metadata": response.metadata.model_copy(update={"cached": True}),
            },
            deep=True,
        )

    @staticmethod
    def _parse_prediction_date(value: str) -> date | None:
        """Best-effort parse of prediction labels into plain dates for charting."""

        try:
            return date.fromisoformat(value)
        except ValueError:
            pass

        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None

    def _select_anomalies(
        self,
        *,
        predictions: tuple[PredictionPoint, ...],
        rmse: float,
    ) -> tuple[ResolvedPredictionAnomaly, ...]:
        """Return the largest validation misses that deserve contextual review."""

        resolved: list[ResolvedPredictionAnomaly] = []
        for prediction in predictions:
            prediction_date = self._parse_prediction_date(prediction.row_label)
            if prediction_date is None:
                continue

            residual = prediction.actual - prediction.predicted
            resolved.append(
                ResolvedPredictionAnomaly(
                    date=prediction_date,
                    actual=prediction.actual,
                    predicted=prediction.predicted,
                    residual=residual,
                    absolute_residual=abs(residual),
                    anomaly_threshold=0.0,
                )
            )

        if not resolved:
            return ()

        absolute_residuals = sorted(
            anomaly.absolute_residual for anomaly in resolved
        )
        percentile_index = max(int(len(absolute_residuals) * 0.9) - 1, 0)
        percentile_threshold = absolute_residuals[percentile_index]
        anomaly_threshold = max(rmse * 1.75, percentile_threshold)

        selected = [
            ResolvedPredictionAnomaly(
                date=anomaly.date,
                actual=anomaly.actual,
                predicted=anomaly.predicted,
                residual=anomaly.residual,
                absolute_residual=anomaly.absolute_residual,
                anomaly_threshold=anomaly_threshold,
            )
            for anomaly in resolved
            if anomaly.absolute_residual >= anomaly_threshold
        ]

        if not selected:
            largest = max(resolved, key=lambda anomaly: anomaly.absolute_residual)
            if largest.absolute_residual < rmse * 1.25:
                return ()

            selected = [
                ResolvedPredictionAnomaly(
                    date=largest.date,
                    actual=largest.actual,
                    predicted=largest.predicted,
                    residual=largest.residual,
                    absolute_residual=largest.absolute_residual,
                    anomaly_threshold=anomaly_threshold,
                )
            ]

        selected.sort(key=lambda anomaly: anomaly.absolute_residual, reverse=True)
        return tuple(selected[: self._news_service.max_anomaly_days])

    @staticmethod
    def _serialize_anomaly(
        *,
        anomaly: ResolvedPredictionAnomaly,
        news_articles: tuple[NewsArticle, ...],
    ) -> PredictionAnomalyResponse:
        """Convert an internal anomaly into the API response contract."""

        return PredictionAnomalyResponse(
            date=anomaly.date,
            actual=anomaly.actual,
            predicted=anomaly.predicted,
            residual=anomaly.residual,
            absolute_residual=anomaly.absolute_residual,
            anomaly_threshold=anomaly.anomaly_threshold,
            news=[
                NewsArticleResponse(
                    title=article.title,
                    url=article.url,
                    source=article.source,
                    summary=article.summary,
                    published_at=article.published_at,
                )
                for article in news_articles
            ],
        )

    @staticmethod
    def _subtract_years(value: date, years: int) -> date:
        """Subtract whole years while preserving valid calendar dates."""

        try:
            return value.replace(year=value.year - years)
        except ValueError:
            return value.replace(month=2, day=28, year=value.year - years)

    @staticmethod
    def _default_generated_at() -> datetime:
        """Return a timezone-aware UTC timestamp for API metadata."""

        return datetime.now(timezone.utc)

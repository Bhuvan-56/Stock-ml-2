"""Dependency providers for FastAPI routes."""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Request

from stockml.core.config import Settings
from stockml.domain.protocols import (
    FeatureEngineer,
    ModelTrainer,
    NewsSearchProvider,
    StockDataProvider,
)
from stockml.infrastructure.news.tavily_client import TavilyNewsProvider
from stockml.infrastructure.market_data.yfinance_client import YFinanceStockDataProvider
from stockml.ml.feature_engineering import RollingWindowFeatureEngineer
from stockml.ml.pipeline import PredictionPipeline
from stockml.ml.trainer import SklearnMLPTrainer
from stockml.services.health_service import HealthService
from stockml.services.news_service import NewsService
from stockml.services.prediction_service import PredictionResultCache, PredictionService
from stockml.services.stock_data_service import StockDataService


def get_app_settings(request: Request) -> Settings:
    """Return the typed settings instance attached to the FastAPI app."""

    return cast(Settings, request.app.state.settings)


def get_prediction_cache(request: Request) -> PredictionResultCache:
    """Return the shared prediction cache attached to the app instance."""

    return cast(PredictionResultCache, request.app.state.prediction_cache)


def get_stock_data_provider(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> StockDataProvider:
    """Create the configured market-data provider."""

    return YFinanceStockDataProvider(settings=settings.market_data)


def get_stock_data_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    provider: Annotated[StockDataProvider, Depends(get_stock_data_provider)],
) -> StockDataService:
    """Create the stock market history application service."""

    return StockDataService(provider=provider, settings=settings.market_data)


def get_feature_engineer() -> FeatureEngineer:
    """Return the default rolling-window feature engineer."""

    return RollingWindowFeatureEngineer()


def get_news_provider(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> NewsSearchProvider | None:
    """Create the configured contextual news provider when enabled."""

    if not settings.news.enabled or not settings.news.has_api_key:
        return None

    return TavilyNewsProvider(settings=settings.news)


def get_news_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    provider: Annotated[NewsSearchProvider | None, Depends(get_news_provider)],
) -> NewsService:
    """Create the contextual news service for anomaly enrichment."""

    return NewsService(settings=settings.news, provider=provider)


def get_model_trainer(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ModelTrainer:
    """Create the configured model trainer."""

    return SklearnMLPTrainer(settings=settings.model)


def get_prediction_pipeline(
    settings: Annotated[Settings, Depends(get_app_settings)],
    feature_engineer: Annotated[FeatureEngineer, Depends(get_feature_engineer)],
    trainer: Annotated[ModelTrainer, Depends(get_model_trainer)],
) -> PredictionPipeline:
    """Create the prediction pipeline for the current request."""

    return PredictionPipeline(
        feature_engineer=feature_engineer,
        trainer=trainer,
        settings=settings.model,
    )


def get_prediction_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
    stock_data_service: Annotated[StockDataService, Depends(get_stock_data_service)],
    prediction_pipeline: Annotated[PredictionPipeline, Depends(get_prediction_pipeline)],
    news_service: Annotated[NewsService, Depends(get_news_service)],
    cache: Annotated[PredictionResultCache, Depends(get_prediction_cache)],
) -> PredictionService:
    """Create the top-level prediction service."""

    return PredictionService(
        stock_data_service=stock_data_service,
        prediction_pipeline=prediction_pipeline,
        market_data_settings=settings.market_data,
        news_service=news_service,
        cache=cache,
    )


def get_health_service(
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> HealthService:
    """Build the health service for the current request."""

    return HealthService(settings=settings)

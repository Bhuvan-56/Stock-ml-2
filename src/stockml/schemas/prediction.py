"""API schemas for prediction requests and responses."""

from __future__ import annotations

import re
from datetime import date as DateType
from datetime import datetime as DateTimeType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-^]{1,16}$")


class PredictionRequest(BaseModel):
    """Validated request payload for stock prediction generation."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    symbol: str = Field(min_length=1, max_length=16)
    start_date: DateType | None = None
    end_date: DateType | None = None

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        """Normalize supported ticker symbols into uppercase exchange format."""

        normalized_value = value.strip().upper()
        if not normalized_value:
            raise ValueError("symbol must not be blank.")
        if not SYMBOL_PATTERN.fullmatch(normalized_value):
            raise ValueError(
                "symbol may only contain letters, numbers, '.', '-', and '^' characters."
            )
        return normalized_value

    @model_validator(mode="after")
    def validate_window(self) -> "PredictionRequest":
        """Reject inverted date windows before hitting the service layer."""

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError("start_date must be less than or equal to end_date.")
        return self


class PredictionStockWindow(BaseModel):
    """Normalized date-window metadata for the prediction response."""

    model_config = ConfigDict(extra="forbid")

    requested_start_date: DateType
    requested_end_date: DateType
    actual_start_date: DateType
    actual_end_date: DateType
    interval: str
    row_count: int = Field(ge=1)


class PredictionMetricsResponse(BaseModel):
    """Metrics describing the validation performance of the generated model."""

    model_config = ConfigDict(extra="forbid")

    mae: float = Field(ge=0.0)
    rmse: float = Field(ge=0.0)
    training_rows: int = Field(ge=1)
    validation_rows: int = Field(ge=1)
    feature_count: int = Field(ge=1)


class HistoricalPricePointResponse(BaseModel):
    """Historical price point returned for UI charting and inspection."""

    model_config = ConfigDict(extra="forbid")

    date: DateType
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(ge=0)


class PredictionPointResponse(BaseModel):
    """Predicted and actual values for a validation point."""

    model_config = ConfigDict(extra="forbid")

    label: str
    date: DateType | None = None
    actual: float
    predicted: float
    residual: float


class NewsArticleResponse(BaseModel):
    """Contextual news article returned for an anomaly day."""

    model_config = ConfigDict(extra="forbid")

    title: str
    url: str
    source: str
    summary: str | None = None
    published_at: DateTimeType | None = None


class PredictionAnomalyResponse(BaseModel):
    """Large validation miss that may warrant contextual news review."""

    model_config = ConfigDict(extra="forbid")

    date: DateType
    actual: float
    predicted: float
    residual: float
    absolute_residual: float = Field(ge=0.0)
    anomaly_threshold: float = Field(ge=0.0)
    news: list[NewsArticleResponse]


class PredictionMetadataResponse(BaseModel):
    """Metadata that helps the client explain the prediction result."""

    model_config = ConfigDict(extra="forbid")

    model_name: str
    target_column: str
    source: str
    generated_at: DateTimeType
    cached: bool
    prediction_count: int = Field(ge=0)
    anomaly_count: int = Field(ge=0)
    news_status: Literal["disabled", "ready", "unavailable"]
    news_provider: str | None = None


class PredictionResponse(BaseModel):
    """Top-level prediction payload consumed by the frontend."""

    model_config = ConfigDict(extra="forbid")

    symbol: str
    stock_window: PredictionStockWindow
    feature_columns: list[str]
    metrics: PredictionMetricsResponse
    price_history: list[HistoricalPricePointResponse]
    predictions: list[PredictionPointResponse]
    anomalies: list[PredictionAnomalyResponse]
    metadata: PredictionMetadataResponse

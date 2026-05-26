"""Typed domain models for ML training and prediction workflows."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True, slots=True)
class FeatureSet:
    """Feature-engineered dataset ready for train/validation splitting."""

    feature_frame: pd.DataFrame
    target_series: pd.Series
    feature_columns: tuple[str, ...]
    target_column: str

    def __post_init__(self) -> None:
        if self.feature_frame.empty:
            raise ValueError("Feature frame must contain at least one row.")
        if not self.feature_columns:
            raise ValueError("Feature columns must not be empty.")
        if len(self.feature_frame) != len(self.target_series):
            raise ValueError("Feature and target rows must match.")
        if not self.feature_frame.index.equals(self.target_series.index):
            raise ValueError("Feature and target indices must align.")
        if tuple(self.feature_frame.columns) != self.feature_columns:
            raise ValueError("Feature frame columns must match feature_columns exactly.")

    @property
    def row_count(self) -> int:
        """Return the number of usable rows."""

        return len(self.feature_frame)


@dataclass(frozen=True, slots=True)
class DatasetSplit:
    """A chronological train/validation split of engineered features."""

    train_features: pd.DataFrame
    train_target: pd.Series
    validation_features: pd.DataFrame
    validation_target: pd.Series
    feature_columns: tuple[str, ...]
    target_column: str

    def __post_init__(self) -> None:
        if self.train_features.empty:
            raise ValueError("Training features must contain at least one row.")
        if self.validation_features.empty:
            raise ValueError("Validation features must contain at least one row.")
        if len(self.train_features) != len(self.train_target):
            raise ValueError("Training feature and target rows must match.")
        if len(self.validation_features) != len(self.validation_target):
            raise ValueError("Validation feature and target rows must match.")
        if not self.train_features.index.equals(self.train_target.index):
            raise ValueError("Training feature and target indices must align.")
        if not self.validation_features.index.equals(self.validation_target.index):
            raise ValueError("Validation feature and target indices must align.")
        if tuple(self.train_features.columns) != self.feature_columns:
            raise ValueError("Training feature columns must match feature_columns exactly.")
        if tuple(self.validation_features.columns) != self.feature_columns:
            raise ValueError("Validation feature columns must match feature_columns exactly.")

    @property
    def training_rows(self) -> int:
        """Return the number of training rows."""

        return len(self.train_features)

    @property
    def validation_rows(self) -> int:
        """Return the number of validation rows."""

        return len(self.validation_features)


@dataclass(frozen=True, slots=True)
class PredictionPoint:
    """A single validation prediction paired with the source row label."""

    row_label: str
    actual: float
    predicted: float


@dataclass(frozen=True, slots=True)
class TrainingMetrics:
    """Summary metrics for a completed training run."""

    mae: float
    rmse: float
    training_rows: int
    validation_rows: int
    feature_count: int


@dataclass(frozen=True, slots=True)
class ModelTrainingResult:
    """Structured training output returned by the ML layer."""

    model_name: str
    target_column: str
    feature_columns: tuple[str, ...]
    metrics: TrainingMetrics
    predictions: tuple[PredictionPoint, ...]

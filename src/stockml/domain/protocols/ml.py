"""Protocols for ML pipeline collaboration points."""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from stockml.domain.models import DatasetSplit, FeatureSet, ModelTrainingResult


class FeatureEngineer(Protocol):
    """Transform raw market history into model-ready features."""

    def build_feature_set(self, market_history: pd.DataFrame) -> FeatureSet:
        """Return engineered features and the target series for training."""


class ModelTrainer(Protocol):
    """Fit a regression model and produce structured validation output."""

    def train(self, dataset_split: DatasetSplit) -> ModelTrainingResult:
        """Train the model and return validation predictions plus metrics."""

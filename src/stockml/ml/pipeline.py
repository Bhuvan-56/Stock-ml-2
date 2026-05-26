"""Prediction pipeline orchestration."""

from __future__ import annotations

import pandas as pd

from stockml.core.config import ModelSettings
from stockml.core.exceptions import TrainingDataError
from stockml.domain.models import DatasetSplit, FeatureSet, ModelTrainingResult
from stockml.domain.protocols import FeatureEngineer, ModelTrainer


class PredictionPipeline:
    """Coordinate feature preparation, dataset splitting, and model training."""

    def __init__(
        self,
        *,
        feature_engineer: FeatureEngineer,
        trainer: ModelTrainer,
        settings: ModelSettings,
    ) -> None:
        self._feature_engineer = feature_engineer
        self._trainer = trainer
        self._settings = settings

    def run(self, market_history: pd.DataFrame) -> ModelTrainingResult:
        """Build features, validate the split, and train the model."""

        feature_set = self._feature_engineer.build_feature_set(market_history)
        dataset_split = self._split_dataset(feature_set)
        return self._trainer.train(dataset_split)

    def _split_dataset(self, feature_set: FeatureSet) -> DatasetSplit:
        """Split engineered features into train and validation windows."""

        row_count = feature_set.row_count
        split_index = int(row_count * self._settings.training_split_ratio)

        if split_index <= 0 or split_index >= row_count:
            raise TrainingDataError(
                "Training split ratio produced an empty train or validation partition."
            )
        if split_index < self._settings.minimum_training_rows:
            raise TrainingDataError(
                "Not enough rows are available for the configured minimum training size."
            )

        return DatasetSplit(
            train_features=feature_set.feature_frame.iloc[:split_index].copy(),
            train_target=feature_set.target_series.iloc[:split_index].copy(),
            validation_features=feature_set.feature_frame.iloc[split_index:].copy(),
            validation_target=feature_set.target_series.iloc[split_index:].copy(),
            feature_columns=feature_set.feature_columns,
            target_column=feature_set.target_column,
        )

"""Trainer implementations for the StockML prediction pipeline."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import StandardScaler

from stockml.core.config import ModelSettings
from stockml.core.exceptions import ModelTrainingError, TrainingDataError
from stockml.domain.models import (
    DatasetSplit,
    ModelTrainingResult,
    PredictionPoint,
    TrainingMetrics,
)


class SklearnMLPTrainer:
    """Train a scaled `MLPRegressor` and return structured validation output."""

    model_name = "mlp_regressor"

    def __init__(self, settings: ModelSettings) -> None:
        self._settings = settings

    def train(self, dataset_split: DatasetSplit) -> ModelTrainingResult:
        """Fit the configured MLP regressor and score the validation window."""

        if dataset_split.training_rows < self._settings.minimum_training_rows:
            raise TrainingDataError(
                "Training split does not satisfy the configured minimum_training_rows."
            )

        estimator = TransformedTargetRegressor(
            regressor=Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        MLPRegressor(
                            hidden_layer_sizes=(self._settings.hidden_units,),
                            activation="relu",
                            solver="adam",
                            max_iter=self._settings.epochs,
                            batch_size=self._settings.batch_size,
                            random_state=self._settings.random_seed,
                            shuffle=False,
                        ),
                    ),
                ]
            ),
            transformer=StandardScaler(),
        )

        try:
            estimator.fit(dataset_split.train_features, dataset_split.train_target)
            predicted_values = np.asarray(
                estimator.predict(dataset_split.validation_features),
                dtype=np.float64,
            )
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise ModelTrainingError("Model training failed.") from exc

        actual_values = np.asarray(dataset_split.validation_target.to_numpy(), dtype=np.float64)
        metrics = TrainingMetrics(
            mae=float(mean_absolute_error(actual_values, predicted_values)),
            rmse=float(np.sqrt(mean_squared_error(actual_values, predicted_values))),
            training_rows=dataset_split.training_rows,
            validation_rows=dataset_split.validation_rows,
            feature_count=len(dataset_split.feature_columns),
        )

        predictions = tuple(
            PredictionPoint(
                row_label=self._format_row_label(row_label),
                actual=float(actual),
                predicted=float(predicted),
            )
            for row_label, actual, predicted in zip(
                dataset_split.validation_features.index,
                actual_values.tolist(),
                predicted_values.tolist(),
                strict=True,
            )
        )

        return ModelTrainingResult(
            model_name=self.model_name,
            target_column=dataset_split.target_column,
            feature_columns=dataset_split.feature_columns,
            metrics=metrics,
            predictions=predictions,
        )

    @staticmethod
    def _format_row_label(value: Any) -> str:
        """Convert a validation index value into a stable string label."""

        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return str(value)

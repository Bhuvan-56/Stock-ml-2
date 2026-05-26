"""Unit tests for ML pipeline orchestration."""

from __future__ import annotations

import pandas as pd
import pytest

from stockml.core.config import ModelSettings
from stockml.core.exceptions import TrainingDataError
from stockml.domain.models import FeatureSet, ModelTrainingResult, TrainingMetrics
from stockml.ml.pipeline import PredictionPipeline


class StubFeatureEngineer:
    """Return a predetermined feature set for pipeline tests."""

    def __init__(self, feature_set: FeatureSet) -> None:
        self.feature_set = feature_set
        self.calls = 0

    def build_feature_set(self, market_history: pd.DataFrame) -> FeatureSet:
        self.calls += 1
        return self.feature_set


class CapturingTrainer:
    """Capture the dataset split passed by the pipeline."""

    def __init__(self, result: ModelTrainingResult) -> None:
        self.result = result
        self.last_split = None

    def train(self, dataset_split):  # type: ignore[no-untyped-def]
        self.last_split = dataset_split
        return self.result


def _build_feature_set(row_count: int = 50) -> FeatureSet:
    index = pd.date_range("2024-01-01", periods=row_count, freq="D")
    feature_frame = pd.DataFrame(
        {
            "momentum": [float(value) for value in range(row_count)],
            "volatility": [float(value) / 10.0 for value in range(row_count)],
        },
        index=index,
    )
    target_series = pd.Series(
        [float(value) * 1.5 for value in range(row_count)],
        index=index,
        name="close",
    )
    return FeatureSet(
        feature_frame=feature_frame,
        target_series=target_series,
        feature_columns=("momentum", "volatility"),
        target_column="close",
    )


def _build_result() -> ModelTrainingResult:
    return ModelTrainingResult(
        model_name="stub",
        target_column="close",
        feature_columns=("momentum", "volatility"),
        metrics=TrainingMetrics(
            mae=0.0,
            rmse=0.0,
            training_rows=35,
            validation_rows=15,
            feature_count=2,
        ),
        predictions=(),
    )


def test_prediction_pipeline_splits_dataset_before_training() -> None:
    feature_engineer = StubFeatureEngineer(_build_feature_set(row_count=50))
    trainer = CapturingTrainer(_build_result())
    pipeline = PredictionPipeline(
        feature_engineer=feature_engineer,
        trainer=trainer,
        settings=ModelSettings(
            training_split_ratio=0.7,
            minimum_training_rows=30,
            hidden_units=8,
            epochs=50,
            batch_size=8,
            random_seed=7,
        ),
    )

    market_history = pd.DataFrame({"close": [10.0, 11.0, 12.0]})
    result = pipeline.run(market_history)

    assert result == trainer.result
    assert feature_engineer.calls == 1
    assert trainer.last_split is not None
    assert trainer.last_split.training_rows == 35
    assert trainer.last_split.validation_rows == 15
    assert trainer.last_split.feature_columns == ("momentum", "volatility")


def test_prediction_pipeline_rejects_insufficient_training_rows() -> None:
    pipeline = PredictionPipeline(
        feature_engineer=StubFeatureEngineer(_build_feature_set(row_count=50)),
        trainer=CapturingTrainer(_build_result()),
        settings=ModelSettings(
            training_split_ratio=0.7,
            minimum_training_rows=40,
            hidden_units=8,
            epochs=50,
            batch_size=8,
            random_seed=7,
        ),
    )

    with pytest.raises(TrainingDataError):
        pipeline.run(pd.DataFrame({"close": [10.0, 11.0, 12.0]}))

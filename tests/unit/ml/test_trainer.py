"""Unit tests for the default MLP trainer."""

from __future__ import annotations

import numpy as np
import pandas as pd

from stockml.core.config import ModelSettings
from stockml.domain.models import DatasetSplit
from stockml.ml.trainer import SklearnMLPTrainer


def _build_dataset_split() -> DatasetSplit:
    rng = np.random.default_rng(7)

    train_features = pd.DataFrame(
        {
            "momentum": rng.normal(loc=0.0, scale=1.0, size=120),
            "volume_shift": rng.normal(loc=0.0, scale=1.0, size=120),
        },
        index=pd.RangeIndex(start=0, stop=120),
    )
    train_target = pd.Series(
        (
            1.8 * train_features["momentum"]
            - 0.6 * train_features["volume_shift"]
            + rng.normal(loc=0.0, scale=0.05, size=120)
        ),
        index=train_features.index,
        name="close",
    )

    validation_features = pd.DataFrame(
        {
            "momentum": rng.normal(loc=0.0, scale=1.0, size=30),
            "volume_shift": rng.normal(loc=0.0, scale=1.0, size=30),
        },
        index=pd.RangeIndex(start=120, stop=150),
    )
    validation_target = pd.Series(
        (
            1.8 * validation_features["momentum"]
            - 0.6 * validation_features["volume_shift"]
            + rng.normal(loc=0.0, scale=0.05, size=30)
        ),
        index=validation_features.index,
        name="close",
    )

    return DatasetSplit(
        train_features=train_features,
        train_target=train_target,
        validation_features=validation_features,
        validation_target=validation_target,
        feature_columns=("momentum", "volume_shift"),
        target_column="close",
    )


def test_sklearn_mlp_trainer_returns_structured_predictions() -> None:
    trainer = SklearnMLPTrainer(
        ModelSettings(
            training_split_ratio=0.8,
            minimum_training_rows=60,
            hidden_units=16,
            epochs=500,
            batch_size=16,
            random_seed=7,
        )
    )

    result = trainer.train(_build_dataset_split())

    assert result.model_name == "mlp_regressor"
    assert result.target_column == "close"
    assert result.feature_columns == ("momentum", "volume_shift")
    assert result.metrics.training_rows == 120
    assert result.metrics.validation_rows == 30
    assert result.metrics.feature_count == 2
    assert len(result.predictions) == 30
    assert result.metrics.mae < 0.35
    assert result.metrics.rmse < 0.45
    assert result.predictions[0].row_label == "120"

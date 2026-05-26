"""Pydantic schema package for API contracts."""

from .health import HealthResponse
from .prediction import PredictionRequest, PredictionResponse

__all__ = ["HealthResponse", "PredictionRequest", "PredictionResponse"]

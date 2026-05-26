"""Prediction endpoint for the StockML API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_prediction_service
from stockml.schemas.prediction import PredictionRequest, PredictionResponse
from stockml.services.prediction_service import PredictionService

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post(
    "/",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a stock prediction response",
)
async def create_prediction(
    prediction_request: PredictionRequest,
    prediction_service: Annotated[PredictionService, Depends(get_prediction_service)],
) -> PredictionResponse:
    """Return a typed prediction payload for the requested stock symbol."""

    return await run_in_threadpool(prediction_service.predict, prediction_request)

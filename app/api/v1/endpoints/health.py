"""Health-check endpoint for the StockML API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_health_service
from stockml.schemas.health import HealthResponse
from stockml.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Read backend health status",
)
def read_health(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    """Return backend health metadata for monitoring and smoke tests."""

    return health_service.get_status()

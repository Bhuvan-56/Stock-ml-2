"""Application-specific exception types."""

from __future__ import annotations

from starlette import status


class StockMLError(Exception):
    """Base exception for domain and service-layer failures."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_server_error"

    def __init__(
        self,
        detail: str,
        *,
        error_code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code


class InvalidRequestError(StockMLError):
    """Raised when a request is semantically invalid for the use case."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "invalid_request"


class ResourceNotFoundError(StockMLError):
    """Raised when a requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "resource_not_found"


class UpstreamServiceError(StockMLError):
    """Raised when an external dependency fails."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "upstream_service_error"


class ModelTrainingError(StockMLError):
    """Raised when model fitting or scoring fails unexpectedly."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "model_training_error"


class TrainingDataError(StockMLError):
    """Raised when the ML pipeline does not have enough usable data."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "training_data_error"

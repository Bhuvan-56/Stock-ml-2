"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import build_api_router
from stockml import __version__
from stockml.core.config import Settings, get_settings, resolve_env_files
from stockml.core.exceptions import StockMLError
from stockml.core.logging import configure_logging
from stockml.services.prediction_service import PredictionResultCache

logger = logging.getLogger("stockml.main")


def _build_error_response(
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: list[Any] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def _register_exception_handlers(app: FastAPI) -> None:
    def summarize_exception_cause(exc: BaseException) -> str | None:
        """Return a compact summary of the chained exception cause, if any."""

        current = exc.__cause__ or exc.__context__
        seen: set[int] = set()
        fragments: list[str] = []

        while current is not None and id(current) not in seen:
            seen.add(id(current))
            fragments.append(f"{type(current).__name__}: {current}")
            current = current.__cause__ or current.__context__

        if not fragments:
            return None

        return " <- ".join(fragments)

    @app.exception_handler(StockMLError)
    async def handle_stockml_error(request: Request, exc: StockMLError) -> JSONResponse:
        cause_summary = summarize_exception_cause(exc)
        detail_suffix = "" if cause_summary is None else f" | cause: {cause_summary}"

        if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(
                "Handled application error [%s] for %s %s: %s%s",
                exc.error_code,
                request.method,
                request.url.path,
                exc.detail,
                detail_suffix,
                exc_info=(type(exc), exc, exc.__traceback__),
            )
        else:
            logger.warning(
                "Handled application error [%s] for %s %s: %s%s",
                exc.error_code,
                request.method,
                request.url.path,
                exc.detail,
                detail_suffix,
            )

        return _build_error_response(
            status_code=exc.status_code,
            error_code=exc.error_code,
            message=exc.detail,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _build_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code="request_validation_error",
            message="Request validation failed.",
            details=jsonable_encoder(list(exc.errors())),
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        _: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error."
        return _build_error_response(
            status_code=exc.status_code,
            error_code="http_error",
            message=message,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error", exc_info=exc)
        return _build_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="internal_server_error",
            message="An unexpected error occurred.",
        )


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    resolved_settings = settings or get_settings()
    configure_logging(resolved_settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "Starting %s in %s mode",
            resolved_settings.app_name,
            resolved_settings.environment,
        )
        logger.info(
            "Configuration env files: %s",
            ", ".join(str(path) for path in resolve_env_files()),
        )
        logger.info(
            "News enrichment status: enabled=%s provider=%s api_key=%s",
            resolved_settings.news.enabled,
            resolved_settings.news.provider,
            "configured" if resolved_settings.news.has_api_key else "missing",
        )
        yield
        logger.info("Stopping %s", resolved_settings.app_name)

    app = FastAPI(
        title=resolved_settings.app_name,
        debug=resolved_settings.debug,
        version=__version__,
        lifespan=lifespan,
        openapi_url=f"{resolved_settings.api.prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.state.settings = resolved_settings
    app.state.prediction_cache = PredictionResultCache()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(build_api_router(resolved_settings.api.prefix))
    _register_exception_handlers(app)
    return app


app = create_app()

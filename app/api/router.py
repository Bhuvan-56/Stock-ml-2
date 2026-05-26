"""Top-level API router composition."""

from fastapi import APIRouter

from app.api.v1.router import router as v1_router


def build_api_router(api_prefix: str) -> APIRouter:
    """Create the root API router with the configured prefix."""

    router = APIRouter()
    router.include_router(v1_router, prefix=api_prefix)
    return router

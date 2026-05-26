"""Logging configuration helpers."""

from __future__ import annotations

import logging
from logging.config import dictConfig

from stockml.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure application and framework logging."""

    level = "DEBUG" if settings.debug else settings.log_level

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": level,
                }
            },
            "root": {
                "handlers": ["default"],
                "level": level,
            },
            "loggers": {
                "stockml": {
                    "handlers": ["default"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn": {
                    "handlers": ["default"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["default"],
                    "level": level,
                    "propagate": False,
                },
                "yfinance": {
                    "handlers": ["default"],
                    "level": "CRITICAL",
                    "propagate": False,
                },
            },
        }
    )

    logging.captureWarnings(True)

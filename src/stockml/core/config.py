"""Typed environment-driven configuration for the StockML backend."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["local", "development", "test", "staging", "production"]
LogLevelName = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

_CONFIG_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CONFIG_DIR.parents[2]


def resolve_env_files(
    *,
    project_root: Path = _PROJECT_ROOT,
    config_dir: Path = _CONFIG_DIR,
) -> tuple[Path, ...]:
    """Return the env files to load, preferring the project root when present.

    The canonical location remains the repository root. A colocated fallback
    keeps local development forgiving when only ``src/stockml/core/.env`` exists.
    """

    root_env_files = (project_root / ".env", project_root / ".env.local")
    config_env_files = (config_dir / ".env", config_dir / ".env.local")

    if any(path.exists() for path in root_env_files):
        return root_env_files

    return config_env_files


class ApiSettings(BaseModel):
    """Settings for HTTP delivery."""

    prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    reload: bool = False
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )


class MarketDataSettings(BaseModel):
    """Settings for stock market data retrieval."""

    provider: Literal["yfinance"] = "yfinance"
    interval: Literal["1d"] = "1d"
    default_history_years: int = Field(default=3, ge=1, le=20)
    request_timeout_seconds: int = Field(default=30, ge=1, le=300)
    request_retries: int = Field(default=1, ge=0, le=3)
    cache_directory: str = ".cache/yfinance"


class NewsSettings(BaseModel):
    """Settings for anomaly-news retrieval."""

    enabled: bool = True
    provider: Literal["tavily"] = "tavily"
    tavily_api_key: SecretStr | None = None
    request_timeout_seconds: int = Field(default=8, ge=1, le=60)
    max_articles_per_anomaly: int = Field(default=3, ge=1, le=10)
    max_anomaly_days: int = Field(default=2, ge=1, le=5)

    @property
    def has_api_key(self) -> bool:
        """Return whether a usable Tavily API key is configured."""

        return bool(
            self.tavily_api_key is not None
            and self.tavily_api_key.get_secret_value().strip()
        )


class ModelSettings(BaseModel):
    """Settings that shape model training defaults."""

    training_split_ratio: float = Field(default=0.8, gt=0.0, lt=1.0)
    minimum_training_rows: int = Field(default=60, ge=30)
    hidden_units: int = Field(default=64, ge=1, le=2048)
    epochs: int = Field(default=100, ge=1, le=10000)
    batch_size: int = Field(default=32, ge=1, le=4096)
    random_seed: int = 42


class Settings(BaseSettings):
    """Application settings loaded from environment variables and env files."""

    model_config = SettingsConfigDict(
        env_file=resolve_env_files(),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="STOCKML_",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    app_name: str = "StockML API"
    environment: EnvironmentName = "local"
    debug: bool = False
    log_level: LogLevelName = "INFO"
    api: ApiSettings = Field(default_factory=ApiSettings)
    market_data: MarketDataSettings = Field(default_factory=MarketDataSettings)
    news: NewsSettings = Field(default_factory=NewsSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)

    @property
    def is_production(self) -> bool:
        """Return whether the application is running in production."""

        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Return whether the application is running in a local-style environment."""

        return self.environment in {"local", "development"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings object for application-wide reuse."""

    return Settings()

"""Tests for typed environment configuration."""

from __future__ import annotations

from pathlib import Path

import pytest

from stockml.core.config import Settings, get_settings, resolve_env_files


def test_settings_use_expected_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.app_name == "StockML API"
    assert settings.environment == "local"
    assert settings.debug is False
    assert settings.api.port == 8000
    assert settings.market_data.default_history_years == 3
    assert settings.model.training_split_ratio == 0.8


def test_settings_read_nested_environment_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("STOCKML_ENVIRONMENT", "test")
    monkeypatch.setenv("STOCKML_DEBUG", "true")
    monkeypatch.setenv("STOCKML_API__PORT", "9001")
    monkeypatch.setenv("STOCKML_MARKET_DATA__DEFAULT_HISTORY_YEARS", "5")
    monkeypatch.setenv("STOCKML_MODEL__EPOCHS", "250")

    settings = Settings(_env_file=None)

    assert settings.environment == "test"
    assert settings.debug is True
    assert settings.api.port == 9001
    assert settings.market_data.default_history_years == 5
    assert settings.model.epochs == 250


def test_get_settings_returns_cached_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("STOCKML_ENVIRONMENT", "test")

    first = get_settings()
    second = get_settings()

    assert first is second
    assert first.environment == "test"

    get_settings.cache_clear()


def test_resolve_env_files_prefers_project_root(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config_dir = workspace / "src" / "stockml" / "core"
    config_dir.mkdir(parents=True)
    root_env = workspace / ".env"
    root_env_local = workspace / ".env.local"
    config_env = config_dir / ".env"
    config_env_local = config_dir / ".env.local"

    root_env.write_text("STOCKML_ENVIRONMENT=production\n", encoding="utf-8")
    config_env.write_text("STOCKML_ENVIRONMENT=local\n", encoding="utf-8")

    assert resolve_env_files(project_root=workspace, config_dir=config_dir) == (
        root_env,
        root_env_local,
    )
    assert config_env_local not in resolve_env_files(
        project_root=workspace,
        config_dir=config_dir,
    )


def test_resolve_env_files_falls_back_to_config_directory(
    tmp_path: Path,
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    config_dir = workspace / "src" / "stockml" / "core"
    config_dir.mkdir(parents=True)
    config_env = config_dir / ".env"
    config_env_local = config_dir / ".env.local"

    config_env.write_text("STOCKML_NEWS__ENABLED=true\n", encoding="utf-8")

    assert resolve_env_files(project_root=workspace, config_dir=config_dir) == (
        config_env,
        config_env_local,
    )

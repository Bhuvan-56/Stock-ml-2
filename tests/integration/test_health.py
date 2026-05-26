"""Integration tests for the FastAPI server foundation."""

from __future__ import annotations

from fastapi.testclient import TestClient

from stockml.core.exceptions import UpstreamServiceError
from stockml import main as main_module
from stockml.core.config import Settings
from stockml.main import create_app


def test_health_endpoint_returns_expected_metadata() -> None:
    app = create_app(Settings(_env_file=None, environment="test"))

    with TestClient(app) as client:
        response = client.get("/api/v1/health/")

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "StockML API"
    assert payload["environment"] == "test"
    assert payload["version"] == "0.1.0"
    assert payload["timestamp"].endswith("Z")


def test_unknown_route_uses_consistent_error_shape() -> None:
    app = create_app(Settings(_env_file=None, environment="test"))

    with TestClient(app) as client:
        response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "http_error",
            "message": "Not Found",
        }
    }


def test_stockml_error_handler_logs_server_side_cause(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    app = create_app(Settings(_env_file=None, environment="test"))
    logged: dict[str, object] = {}

    def fake_error(message, *args, **kwargs):  # type: ignore[no-untyped-def]
        logged["message"] = message % args if args else message
        logged["kwargs"] = kwargs

    def boom() -> None:
        try:
            raise TimeoutError("curl: (28) Connection timed out")
        except TimeoutError as exc:
            raise UpstreamServiceError(
                "Yahoo Finance timed out while loading symbol 'NFLX'."
            ) from exc

    app.add_api_route("/_test/upstream-error", boom, methods=["GET"])
    monkeypatch.setattr(main_module.logger, "error", fake_error)

    with TestClient(app) as client:
        response = client.get("/_test/upstream-error")

    assert response.status_code == 502
    assert response.json()["error"]["message"] == "Yahoo Finance timed out while loading symbol 'NFLX'."
    assert "Handled application error [upstream_service_error]" in str(logged["message"])
    assert "curl: (28) Connection timed out" in str(logged["message"])

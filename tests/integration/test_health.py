"""Integration tests for health readiness endpoint."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_ok_when_db_reachable(tmp_path: Path) -> None:
    """Return healthy status when SQLite is reachable."""

    db_path = tmp_path / "health.db"
    app = create_app(Settings(db_path=str(db_path)))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_degraded_when_db_unavailable(tmp_path: Path) -> None:
    """Return degraded status when SQLite path is invalid."""

    missing_dir = tmp_path / "missing" / "nested"
    app = create_app(Settings(db_path=str(missing_dir / "health.db")))
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["error_code"] == "DB_UNAVAILABLE"

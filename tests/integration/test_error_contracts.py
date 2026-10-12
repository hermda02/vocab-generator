"""Integration tests for deterministic error contracts."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write a valid dataset fixture for error-path setup.

    Parameters
    ----------
    path : Path
        Filesystem path where fixture content should be written.
    """

    fixture_entries = [
        {
            "word_id": "no-001",
            "norwegian_word": "havn",
            "english_word": "harbor",
            "norwegian_definition": "Et beskyttet omrade for skip.",
            "english_definition": "A sheltered place for ships.",
        }
    ]
    path.write_text(json.dumps(fixture_entries), encoding="utf-8")


def test_get_word_returns_dataset_unavailable_when_dataset_missing(tmp_path: Path) -> None:
    """Return DATASET_UNAVAILABLE when dataset file cannot be loaded."""

    db_path = tmp_path / "service.db"
    missing_dataset_path = tmp_path / "missing-dataset.json"

    app = create_app(Settings(db_path=str(db_path), dataset_path=str(missing_dataset_path)))
    client = TestClient(app)

    response = client.get("/word")

    assert response.status_code == 500
    payload = response.json()
    assert payload["error_code"] == "DATASET_UNAVAILABLE"
    assert payload["status"] == "degraded"


def test_get_word_returns_db_unavailable_when_db_path_invalid(tmp_path: Path) -> None:
    """Return DB_UNAVAILABLE when the database path cannot be opened."""

    dataset_path = tmp_path / "dataset.json"
    _write_dataset(dataset_path)
    invalid_db_path = tmp_path / "missing" / "nested" / "service.db"

    app = create_app(Settings(db_path=str(invalid_db_path), dataset_path=str(dataset_path)))
    client = TestClient(app)

    response = client.get("/word")

    assert response.status_code == 503
    payload = response.json()
    assert payload["error_code"] == "DB_UNAVAILABLE"
    assert payload["status"] == "degraded"

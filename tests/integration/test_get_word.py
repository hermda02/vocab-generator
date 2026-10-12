"""Integration tests for active-word retrieval endpoint."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write a minimal valid vocabulary dataset fixture.

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


def test_get_word_returns_required_payload_fields(tmp_path: Path) -> None:
    """Return all required fields when no active word is present."""

    db_path = tmp_path / "service.db"
    dataset_path = tmp_path / "dataset.json"
    _write_dataset(dataset_path)

    app = create_app(Settings(db_path=str(db_path), dataset_path=str(dataset_path)))
    client = TestClient(app)

    response = client.get("/word")

    assert response.status_code == 200
    payload = response.json()
    assert payload["word_id"] == "no-001"
    assert payload["norwegian_word"] == "havn"
    assert payload["english_word"] == "harbor"
    assert payload["norwegian_definition"]
    assert payload["english_definition"]
    assert payload["cycle_id"] == 1
    assert isinstance(payload["generated_at"], str)


def test_get_word_returns_same_active_word_on_repeat_calls(tmp_path: Path) -> None:
    """Return stable active-word payload until refresh endpoint is introduced."""

    db_path = tmp_path / "service.db"
    dataset_path = tmp_path / "dataset.json"
    _write_dataset(dataset_path)

    app = create_app(Settings(db_path=str(db_path), dataset_path=str(dataset_path)))
    client = TestClient(app)

    first_response = client.get("/word")
    second_response = client.get("/word")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json() == first_response.json()

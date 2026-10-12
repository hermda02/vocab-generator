"""Integration tests for forced refresh endpoint."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write a dataset fixture for refresh behavior tests.

    Parameters
    ----------
    path : Path
        Target path for dataset fixture.
    """

    fixture_entries = [
        {
            "word_id": "no-001",
            "norwegian_word": "havn",
            "english_word": "harbor",
            "norwegian_definition": "Et beskyttet omrade for skip.",
            "english_definition": "A sheltered place for ships.",
        },
        {
            "word_id": "no-002",
            "norwegian_word": "skog",
            "english_word": "forest",
            "norwegian_definition": "Et stort omrade med trer.",
            "english_definition": "A large area with trees.",
        },
    ]
    path.write_text(json.dumps(fixture_entries), encoding="utf-8")


def _write_seed_words(path: Path) -> None:
    """Write a non-matching seed file so baseline seeding does not consume fixture.

    Parameters
    ----------
    path : Path
        Target path for seed fixture.
    """

    path.write_text("og\n", encoding="utf-8")


def test_post_new_word_replaces_active_word(tmp_path: Path) -> None:
    """Return a new active word when refresh endpoint is called."""

    db_path = tmp_path / "service.db"
    dataset_path = tmp_path / "dataset.json"
    seed_path = tmp_path / "seed.txt"
    _write_dataset(dataset_path)
    _write_seed_words(seed_path)

    app = create_app(
        Settings(
            db_path=str(db_path),
            dataset_path=str(dataset_path),
            seed_words_path=str(seed_path),
        )
    )
    client = TestClient(app)

    first_word = client.get("/word")
    refreshed_word = client.post("/word/new")
    current_word = client.get("/word")

    assert first_word.status_code == 200
    assert refreshed_word.status_code == 200
    assert current_word.status_code == 200

    first_payload = first_word.json()
    refreshed_payload = refreshed_word.json()
    current_payload = current_word.json()

    assert refreshed_payload["word_id"] != first_payload["word_id"]
    assert current_payload["word_id"] == refreshed_payload["word_id"]

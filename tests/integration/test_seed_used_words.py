"""Integration tests for baseline pre-used seed behavior."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write a dataset fixture with one seeded and one non-seeded word.

    Parameters
    ----------
    path : Path
        Target path for JSON dataset fixture.
    """

    fixture_entries = [
        {
            "word_id": "no-seeded",
            "norwegian_word": "og",
            "english_word": "and",
            "norwegian_definition": "Konjunksjon som binder sammen ord.",
            "english_definition": "Conjunction that connects words.",
        },
        {
            "word_id": "no-fresh",
            "norwegian_word": "havn",
            "english_word": "harbor",
            "norwegian_definition": "Et beskyttet omrade langs kysten.",
            "english_definition": "A sheltered coastal area.",
        },
    ]
    path.write_text(json.dumps(fixture_entries), encoding="utf-8")


def _write_seed_words(path: Path) -> None:
    """Write a minimal baseline seed list fixture.

    Parameters
    ----------
    path : Path
        Target path for seed file.
    """

    path.write_text("og\n", encoding="utf-8")


def test_seed_words_are_initialized_as_used_and_excluded(tmp_path: Path) -> None:
    """Exclude seeded words from first active-word selection."""

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

    response = client.get("/word")

    assert response.status_code == 200
    payload = response.json()
    assert payload["word_id"] == "no-fresh"

    with sqlite3.connect(db_path) as connection:
        used_rows = connection.execute(
            "SELECT word_id, cycle_id, source FROM used_words"
        ).fetchall()
        metadata_row = connection.execute(
            "SELECT value FROM metadata WHERE key = 'baseline_seeded_cycle_1'"
        ).fetchone()

    assert ("no-seeded", 1, "baseline_top500") in used_rows
    assert metadata_row == ("1",)


def test_seed_initialization_is_idempotent(tmp_path: Path) -> None:
    """Initialize baseline used-word rows exactly once."""

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

    first_response = client.get("/word")
    second_response = client.get("/word")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    with sqlite3.connect(db_path) as connection:
        used_count = connection.execute("SELECT COUNT(*) FROM used_words").fetchone()

    assert used_count == (1,)

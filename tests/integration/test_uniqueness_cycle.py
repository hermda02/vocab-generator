"""Integration tests for uniqueness and cycle reset behavior."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write finite dataset fixture for cycle tests.

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
    """Write a seed file that does not match fixture words.

    Parameters
    ----------
    path : Path
        Target path for seed fixture.
    """

    path.write_text("og\n", encoding="utf-8")


def test_cycle_resets_after_all_words_used(tmp_path: Path, caplog) -> None:
    """Increment cycle ID when all words in finite dataset are consumed."""

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
    caplog.set_level(logging.INFO, logger="vocab_generator")
    client = TestClient(app)

    first_word = client.get("/word")
    second_word = client.post("/word/new")
    third_word = client.post("/word/new")

    assert first_word.status_code == 200
    assert second_word.status_code == 200
    assert third_word.status_code == 200

    first_payload = first_word.json()
    second_payload = second_word.json()
    third_payload = third_word.json()

    assert second_payload["word_id"] != first_payload["word_id"]
    assert third_payload["cycle_id"] == 2
    assert third_payload["word_id"] in {"no-001", "no-002"}

    entries = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "vocab_generator"
    ]
    cycle_reset_events = [entry for entry in entries if entry.get("event") == "cycle_reset"]
    assert cycle_reset_events
    assert cycle_reset_events[-1]["cycle_id"] == 2

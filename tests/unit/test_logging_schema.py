"""Unit tests for structured request logging schema."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write a minimal dataset fixture.

    Parameters
    ----------
    path : Path
        Target file path for dataset.
    """

    path.write_text(
        json.dumps(
            [
                {
                    "word_id": "no-001",
                    "norwegian_word": "havn",
                    "english_word": "harbor",
                    "norwegian_definition": "Et beskyttet omrade for skip.",
                    "english_definition": "A sheltered place for ships.",
                }
            ]
        ),
        encoding="utf-8",
    )


def test_request_log_contains_required_fields(tmp_path: Path, caplog) -> None:
    """Emit request log entry with required schema fields."""

    db_path = tmp_path / "service.db"
    dataset_path = tmp_path / "dataset.json"
    seed_path = tmp_path / "seed.txt"
    _write_dataset(dataset_path)
    seed_path.write_text("og\n", encoding="utf-8")

    app = create_app(
        Settings(
            db_path=str(db_path),
            dataset_path=str(dataset_path),
            seed_words_path=str(seed_path),
        )
    )
    caplog.set_level(logging.INFO, logger="vocab_generator")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    entries = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "vocab_generator"
    ]
    request_logs = [entry for entry in entries if entry.get("event") == "request"]
    assert request_logs

    request_log = request_logs[-1]
    assert "timestamp" in request_log
    assert request_log["method"] == "GET"
    assert request_log["path"] == "/health"
    assert request_log["status_code"] == 200
    assert isinstance(request_log["request_id"], str)
    assert isinstance(request_log["latency_ms"], float)


def test_error_response_log_includes_error_code(tmp_path: Path, caplog) -> None:
    """Emit request log entry including machine-readable error code."""

    db_path = tmp_path / "service.db"
    missing_dataset_path = tmp_path / "missing-dataset.json"
    seed_path = tmp_path / "seed.txt"
    seed_path.write_text("og\n", encoding="utf-8")

    app = create_app(
        Settings(
            db_path=str(db_path),
            dataset_path=str(missing_dataset_path),
            seed_words_path=str(seed_path),
        )
    )
    caplog.set_level(logging.INFO, logger="vocab_generator")
    client = TestClient(app)

    response = client.get("/word")

    assert response.status_code == 500
    entries = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "vocab_generator"
    ]
    request_logs = [entry for entry in entries if entry.get("event") == "request"]
    assert request_logs
    assert request_logs[-1]["error_code"] == "DATASET_UNAVAILABLE"

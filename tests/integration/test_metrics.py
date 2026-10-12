"""Integration tests for metrics endpoint payload."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _write_dataset(path: Path) -> None:
    """Write a minimal dataset fixture.

    Parameters
    ----------
    path : Path
        Target path for dataset fixture.
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


def test_metrics_include_request_counts_and_errors(tmp_path: Path) -> None:
    """Expose request counts, error-code counters, and cycle gauge."""

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
    client = TestClient(app)

    client.get("/health")
    client.get("/word")
    client.post("/word/new")
    metrics_response = client.get("/metrics")

    assert metrics_response.status_code == 200
    payload = metrics_response.json()
    assert payload["request_count_by_endpoint"]["/health"] >= 1
    assert payload["request_count_by_endpoint"]["/word"] >= 1
    assert payload["request_count_by_endpoint"]["/word/new"] >= 1
    assert payload["current_cycle_id"] >= 1
    assert isinstance(payload["request_latency_histogram_ms"], dict)


def test_metrics_track_error_code_counts(tmp_path: Path) -> None:
    """Increment error-code counters from failed API requests."""

    db_path = tmp_path / "service.db"
    missing_dataset_path = tmp_path / "missing.json"
    seed_path = tmp_path / "seed.txt"
    seed_path.write_text("og\n", encoding="utf-8")

    app = create_app(
        Settings(
            db_path=str(db_path),
            dataset_path=str(missing_dataset_path),
            seed_words_path=str(seed_path),
        )
    )
    client = TestClient(app)

    error_response = client.get("/word")
    metrics_response = client.get("/metrics")

    assert error_response.status_code == 500
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    assert metrics["error_count_by_code"]["DATASET_UNAVAILABLE"] >= 1

"""FastAPI application entrypoint."""

from __future__ import annotations

import random
import sqlite3
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import Settings, load_settings
from app.dataset import DatasetLoadError, VocabularyEntry, load_dataset
from app.db import check_sqlite_readiness
from app.repository import (
    ActiveWordRecord,
    ensure_schema,
    get_active_word,
    get_current_cycle_id,
    get_used_word_ids,
    increment_current_cycle_id,
    initialize_baseline_used_words,
    mark_word_used,
    upsert_active_word,
)
from app.seed import load_seed_words


def _record_to_payload(record: ActiveWordRecord) -> dict[str, str | int]:
    """Convert a persisted active-word record into API payload shape.

    Parameters
    ----------
    record : ActiveWordRecord
        Active-word record from persistence.

    Returns
    -------
    dict[str, str | int]
        JSON-serializable payload for API responses.
    """

    return {
        "word_id": record.word_id,
        "norwegian_word": record.norwegian_word,
        "english_word": record.english_word,
        "norwegian_definition": record.norwegian_definition,
        "english_definition": record.english_definition,
        "cycle_id": record.cycle_id,
        "generated_at": record.generated_at,
    }


def _degraded_db_response(detail: str | None) -> JSONResponse:
    """Build a deterministic database-unavailable response.

    Parameters
    ----------
    detail : str | None
        Optional technical error detail.

    Returns
    -------
    JSONResponse
        HTTP 503 response payload for DB failures.
    """

    return JSONResponse(
        status_code=503,
        content={
            "status": "degraded",
            "error_code": "DB_UNAVAILABLE",
            "detail": detail,
        },
    )


def _dataset_unavailable_response(detail: str) -> JSONResponse:
    """Build a deterministic dataset-unavailable response.

    Parameters
    ----------
    detail : str
        Technical detail for dataset load failure.

    Returns
    -------
    JSONResponse
        HTTP 500 response payload for dataset failures.
    """

    return JSONResponse(
        status_code=500,
        content={
            "status": "degraded",
            "error_code": "DATASET_UNAVAILABLE",
            "detail": detail,
        },
    )


def _select_first_active_entry(entries: list[VocabularyEntry]) -> VocabularyEntry:
    """Select the initial active entry when none exists in storage.

    Parameters
    ----------
    entries : list[VocabularyEntry]
        Loaded dataset entries.

    Returns
    -------
    VocabularyEntry
        Selected active vocabulary entry.
    """

    return random.choice(entries)


def _select_first_active_entry_excluding_used(
    entries: list[VocabularyEntry],
    used_word_ids: set[str],
) -> VocabularyEntry | None:
    """Select initial active entry excluding words already marked used.

    Parameters
    ----------
    entries : list[VocabularyEntry]
        Loaded dataset entries.
    used_word_ids : set[str]
        Word IDs unavailable for selection in the current cycle.

    Returns
    -------
    VocabularyEntry | None
        Selected entry, or ``None`` if all entries are already used.
    """

    available = [entry for entry in entries if entry.word_id not in used_word_ids]
    if len(available) == 0:
        return None
    return _select_first_active_entry(available)


def _load_generation_inputs(settings: Settings) -> tuple[list[VocabularyEntry], set[str]]:
    """Load dataset and baseline seed words for generation workflows.

    Parameters
    ----------
    settings : Settings
        Runtime application settings.

    Returns
    -------
    tuple[list[VocabularyEntry], set[str]]
        Loaded dataset entries and normalized baseline seed words.

    Raises
    ------
    DatasetLoadError
        Raised when dataset or seed word loading fails.
    """

    return (
        load_dataset(settings.dataset_path),
        load_seed_words(settings.seed_words_path),
    )


def _select_entry_for_cycle(
    db_path: str,
    dataset_entries: list[VocabularyEntry],
    seed_words: set[str],
) -> tuple[VocabularyEntry | None, int]:
    """Select an available entry for the current cycle with reset-on-exhaustion.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.
    dataset_entries : list[VocabularyEntry]
        Dataset entries available for generation.
    seed_words : set[str]
        Normalized baseline seed words.

    Returns
    -------
    tuple[VocabularyEntry | None, int]
        Selected entry and cycle ID used for the selection. Entry is ``None``
        when no selectable entry remains after baseline filtering.
    """

    cycle_id = get_current_cycle_id(db_path)
    initialize_baseline_used_words(
        db_path=db_path,
        dataset_entries=dataset_entries,
        seed_words=seed_words,
        cycle_id=cycle_id,
    )
    used_word_ids = get_used_word_ids(db_path=db_path, cycle_id=cycle_id)
    selected_entry = _select_first_active_entry_excluding_used(dataset_entries, used_word_ids)
    if selected_entry is not None:
        return selected_entry, cycle_id

    next_cycle_id = increment_current_cycle_id(db_path)
    initialize_baseline_used_words(
        db_path=db_path,
        dataset_entries=dataset_entries,
        seed_words=seed_words,
        cycle_id=next_cycle_id,
    )
    used_word_ids = get_used_word_ids(db_path=db_path, cycle_id=next_cycle_id)
    selected_entry = _select_first_active_entry_excluding_used(dataset_entries, used_word_ids)
    return selected_entry, next_cycle_id


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application.

    Parameters
    ----------
    settings : Settings | None
        Optional runtime settings. Defaults to environment-derived settings.

    Returns
    -------
    FastAPI
        Configured FastAPI application.
    """

    resolved_settings = settings or load_settings()
    app = FastAPI(title="Norwegian Vocabulary LAN Service", version="0.1.0")
    app.state.settings = resolved_settings

    @app.get("/health", response_model=None)
    def get_health() -> JSONResponse:
        """Return service and database readiness state.

        Returns
        -------
        JSONResponse | dict[str, str]
            HTTP 200 with ``{"status": "ok"}`` when ready, otherwise
            HTTP 503 with degraded state information.
        """

        is_ready, error_message = check_sqlite_readiness(app.state.settings.db_path)
        if is_ready:
            return JSONResponse(status_code=200, content={"status": "ok"})

        return _degraded_db_response(detail=error_message)

    @app.get("/word", response_model=None)
    def get_word() -> JSONResponse:
        """Return the active vocabulary word payload.

        Returns
        -------
        JSONResponse
            HTTP 200 with active word payload on success, HTTP 503 when the
            database is unavailable, or HTTP 500 when dataset loading fails.
        """

        try:
            ensure_schema(app.state.settings.db_path)
            active_record = get_active_word(app.state.settings.db_path)
            if active_record is not None:
                return JSONResponse(status_code=200, content=_record_to_payload(active_record))
        except sqlite3.Error as exc:
            return _degraded_db_response(detail=str(exc))

        try:
            dataset_entries, seed_words = _load_generation_inputs(app.state.settings)
        except DatasetLoadError as exc:
            return _dataset_unavailable_response(detail=str(exc))

        try:
            selected_entry, cycle_id = _select_entry_for_cycle(
                db_path=app.state.settings.db_path,
                dataset_entries=dataset_entries,
                seed_words=seed_words,
            )
        except sqlite3.Error as exc:
            return _degraded_db_response(detail=str(exc))

        if selected_entry is None:
            return _dataset_unavailable_response(
                detail="No available word remains after baseline seed filtering"
            )
        generated_at = datetime.now(tz=UTC).isoformat()

        try:
            stored_record = upsert_active_word(
                db_path=app.state.settings.db_path,
                entry=selected_entry,
                cycle_id=cycle_id,
                generated_at=generated_at,
            )
        except sqlite3.Error as exc:
            return _degraded_db_response(detail=str(exc))

        return JSONResponse(status_code=200, content=_record_to_payload(stored_record))

    @app.post("/word/new", response_model=None)
    def post_new_word() -> JSONResponse:
        """Replace active word with a newly selected unique entry.

        Returns
        -------
        JSONResponse
            HTTP 200 with new active payload, HTTP 503 for DB failures, or
            HTTP 500 for dataset availability failures.
        """

        try:
            ensure_schema(app.state.settings.db_path)
            active_record = get_active_word(app.state.settings.db_path)
        except sqlite3.Error as exc:
            return _degraded_db_response(detail=str(exc))

        try:
            dataset_entries, seed_words = _load_generation_inputs(app.state.settings)
        except DatasetLoadError as exc:
            return _dataset_unavailable_response(detail=str(exc))

        try:
            if active_record is not None:
                mark_word_used(
                    db_path=app.state.settings.db_path,
                    word_id=active_record.word_id,
                    cycle_id=active_record.cycle_id,
                    source="refresh_previous_active",
                )

            selected_entry, cycle_id = _select_entry_for_cycle(
                db_path=app.state.settings.db_path,
                dataset_entries=dataset_entries,
                seed_words=seed_words,
            )
        except sqlite3.Error as exc:
            return _degraded_db_response(detail=str(exc))

        if selected_entry is None:
            return _dataset_unavailable_response(
                detail="No available word remains after baseline seed filtering"
            )

        generated_at = datetime.now(tz=UTC).isoformat()
        try:
            stored_record = upsert_active_word(
                db_path=app.state.settings.db_path,
                entry=selected_entry,
                cycle_id=cycle_id,
                generated_at=generated_at,
            )
        except sqlite3.Error as exc:
            return _degraded_db_response(detail=str(exc))

        return JSONResponse(status_code=200, content=_record_to_payload(stored_record))

    return app


app = create_app()

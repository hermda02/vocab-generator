"""Persistence helpers for active-word state."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.dataset import VocabularyEntry
from app.seed import normalize_word


@dataclass(frozen=True)
class ActiveWordRecord:
    """Persisted active-word record.

    Parameters
    ----------
    word_id : str
        Stable unique identifier of the selected word.
    norwegian_word : str
        Norwegian word.
    english_word : str
        English equivalent.
    norwegian_definition : str
        Definition in Norwegian.
    english_definition : str
        Definition in English.
    cycle_id : int
        Current generation cycle identifier.
    generated_at : str
        ISO 8601 timestamp for when this word became active.
    """

    word_id: str
    norwegian_word: str
    english_word: str
    norwegian_definition: str
    english_definition: str
    cycle_id: int
    generated_at: str


def ensure_schema(db_path: str) -> None:
    """Ensure the active-word table exists.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.
    """

    active_word_sql = """
    CREATE TABLE IF NOT EXISTS active_word (
        singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
        word_id TEXT NOT NULL,
        norwegian_word TEXT NOT NULL,
        english_word TEXT NOT NULL,
        norwegian_definition TEXT NOT NULL,
        english_definition TEXT NOT NULL,
        cycle_id INTEGER NOT NULL,
        generated_at TEXT NOT NULL
    )
    """
    used_words_sql = """
    CREATE TABLE IF NOT EXISTS used_words (
        word_id TEXT NOT NULL,
        cycle_id INTEGER NOT NULL,
        source TEXT NOT NULL,
        PRIMARY KEY (word_id, cycle_id)
    )
    """
    metadata_sql = """
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        connection.execute(active_word_sql)
        connection.execute(used_words_sql)
        connection.execute(metadata_sql)
        connection.commit()


def initialize_baseline_used_words(
    db_path: str,
    dataset_entries: list[VocabularyEntry],
    seed_words: set[str],
    cycle_id: int,
) -> int:
    """Initialize idempotent baseline used-word records.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.
    dataset_entries : list[VocabularyEntry]
        Dataset entries available for generation.
    seed_words : set[str]
        Normalized baseline word set.

    Returns
    -------
    int
        Number of used-word rows inserted by this call. Returns ``0`` when the
        baseline has already been initialized for this cycle.
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        baseline_key = f"baseline_seeded_cycle_{cycle_id}"
        already_seeded = connection.execute(
            "SELECT value FROM metadata WHERE key = ?",
            (baseline_key,),
        ).fetchone()
        if already_seeded is not None:
            return 0

        matching_word_ids = [
            entry.word_id
            for entry in dataset_entries
            if normalize_word(entry.norwegian_word) in seed_words
        ]
        inserted_count = 0
        for word_id in matching_word_ids:
            connection.execute(
                """
                INSERT OR IGNORE INTO used_words (word_id, cycle_id, source)
                VALUES (?, ?, 'baseline_top500')
                """,
                (word_id, cycle_id),
            )
            inserted_count += 1

        connection.execute(
            "INSERT INTO metadata (key, value) VALUES (?, '1')",
            (baseline_key,),
        )
        connection.commit()

    return inserted_count


def get_used_word_ids(db_path: str, cycle_id: int) -> set[str]:
    """Fetch used word identifiers for the specified cycle.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.
    cycle_id : int
        Cycle identifier to query.

    Returns
    -------
    set[str]
        Word identifiers already marked as used in the cycle.
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        rows = connection.execute(
            "SELECT word_id FROM used_words WHERE cycle_id = ?", (cycle_id,)
        ).fetchall()
    return {row[0] for row in rows}


def mark_word_used(db_path: str, word_id: str, cycle_id: int, source: str) -> None:
    """Mark a word identifier as used for the specified cycle.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.
    word_id : str
        Word identifier to mark as used.
    cycle_id : int
        Cycle identifier.
    source : str
        Origin of the used mark (for observability and debugging).
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO used_words (word_id, cycle_id, source)
            VALUES (?, ?, ?)
            """,
            (word_id, cycle_id, source),
        )
        connection.commit()


def get_current_cycle_id(db_path: str) -> int:
    """Read the current cycle identifier from metadata.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.

    Returns
    -------
    int
        Current cycle identifier. Defaults to ``1`` when unset.
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        row = connection.execute(
            "SELECT value FROM metadata WHERE key = 'current_cycle_id'"
        ).fetchone()
        if row is None:
            connection.execute(
                "INSERT INTO metadata (key, value) VALUES ('current_cycle_id', '1')"
            )
            connection.commit()
            return 1

    return int(row[0])


def increment_current_cycle_id(db_path: str) -> int:
    """Increment and persist the current cycle identifier.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.

    Returns
    -------
    int
        Incremented current cycle identifier.
    """

    current_cycle_id = get_current_cycle_id(db_path)
    next_cycle_id = current_cycle_id + 1
    with sqlite3.connect(db_path, timeout=1.0) as connection:
        connection.execute(
            """
            INSERT INTO metadata (key, value)
            VALUES ('current_cycle_id', ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (str(next_cycle_id),),
        )
        connection.commit()
    return next_cycle_id


def get_active_word(db_path: str) -> ActiveWordRecord | None:
    """Fetch the currently active word, if one exists.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.

    Returns
    -------
    ActiveWordRecord | None
        Persisted active-word record or ``None`` when empty.
    """

    query_sql = """
    SELECT
        word_id,
        norwegian_word,
        english_word,
        norwegian_definition,
        english_definition,
        cycle_id,
        generated_at
    FROM active_word
    WHERE singleton_id = 1
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        row = connection.execute(query_sql).fetchone()

    if row is None:
        return None

    return ActiveWordRecord(
        word_id=row[0],
        norwegian_word=row[1],
        english_word=row[2],
        norwegian_definition=row[3],
        english_definition=row[4],
        cycle_id=row[5],
        generated_at=row[6],
    )


def upsert_active_word(
    db_path: str,
    entry: VocabularyEntry,
    cycle_id: int,
    generated_at: str,
) -> ActiveWordRecord:
    """Persist a new active-word record and return the stored value.

    Parameters
    ----------
    db_path : str
        Filesystem path to SQLite database.
    entry : VocabularyEntry
        Vocabulary entry to persist as active.
    cycle_id : int
        Current cycle identifier.
    generated_at : str
        ISO 8601 timestamp for when this word became active.

    Returns
    -------
    ActiveWordRecord
        Persisted active word record.
    """

    upsert_sql = """
    INSERT INTO active_word (
        singleton_id,
        word_id,
        norwegian_word,
        english_word,
        norwegian_definition,
        english_definition,
        cycle_id,
        generated_at
    ) VALUES (1, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(singleton_id) DO UPDATE SET
        word_id = excluded.word_id,
        norwegian_word = excluded.norwegian_word,
        english_word = excluded.english_word,
        norwegian_definition = excluded.norwegian_definition,
        english_definition = excluded.english_definition,
        cycle_id = excluded.cycle_id,
        generated_at = excluded.generated_at
    """

    with sqlite3.connect(db_path, timeout=1.0) as connection:
        connection.execute(
            upsert_sql,
            (
                entry.word_id,
                entry.norwegian_word,
                entry.english_word,
                entry.norwegian_definition,
                entry.english_definition,
                cycle_id,
                generated_at,
            ),
        )
        connection.commit()

    return ActiveWordRecord(
        word_id=entry.word_id,
        norwegian_word=entry.norwegian_word,
        english_word=entry.english_word,
        norwegian_definition=entry.norwegian_definition,
        english_definition=entry.english_definition,
        cycle_id=cycle_id,
        generated_at=generated_at,
    )

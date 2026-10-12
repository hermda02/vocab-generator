"""SQLite health utilities."""

from __future__ import annotations

import sqlite3


def check_sqlite_readiness(db_path: str) -> tuple[bool, str | None]:
    """Check whether SQLite is reachable for health reporting.

    Parameters
    ----------
    db_path : str
        Filesystem path for the SQLite database.

    Returns
    -------
    tuple[bool, str | None]
        A pair of ``(is_ready, error_message)`` where ``error_message`` is
        ``None`` when readiness checks succeed.
    """

    try:
        with sqlite3.connect(db_path, timeout=1.0) as connection:
            connection.execute("SELECT 1")
    except sqlite3.Error as exc:
        return False, str(exc)

    return True, None

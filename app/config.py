"""Runtime configuration for the service."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables.

    Parameters
    ----------
    app_host : str
        Host interface used by the HTTP server.
    app_port : int
        Port used by the HTTP server.
    db_path : str
        Filesystem path to the SQLite database file.
    dataset_path : str
        Filesystem path to the bundled vocabulary dataset.
    seed_words_path : str
        Filesystem path to baseline pre-used Norwegian words.
    """

    app_host: str = "0.0.0.0"
    app_port: int = 8080
    db_path: str = "/data/vocab.db"
    dataset_path: str = "data/vocabulary.json"
    seed_words_path: str = "data/seed/top500_common_norwegian.txt"


def load_settings() -> Settings:
    """Load settings from environment variables.

    Returns
    -------
    Settings
        Immutable runtime settings.
    """

    return Settings(
        app_host=getenv("APP_HOST", "0.0.0.0"),
        app_port=int(getenv("APP_PORT", "8080")),
        db_path=getenv("DB_PATH", "/data/vocab.db"),
        dataset_path=getenv("DATASET_PATH", "data/vocabulary.json"),
        seed_words_path=getenv(
            "SEED_WORDS_PATH", "data/seed/top500_common_norwegian.txt"
        ),
    )

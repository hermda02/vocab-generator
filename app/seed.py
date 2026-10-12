"""Baseline seed word loading utilities."""

from __future__ import annotations

from pathlib import Path

from app.dataset import DatasetLoadError


def normalize_word(value: str) -> str:
    """Normalize a Norwegian word for matching operations.

    Parameters
    ----------
    value : str
        Raw word value.

    Returns
    -------
    str
        Lowercased alphanumeric word token.
    """

    lowered = value.strip().lower()
    return "".join(char for char in lowered if char.isalpha() or char in {"-", "_"})


def load_seed_words(seed_words_path: str) -> set[str]:
    """Load and normalize baseline pre-used seed words.

    Parameters
    ----------
    seed_words_path : str
        Filesystem path to seed word text file.

    Returns
    -------
    set[str]
        Normalized seed words.

    Raises
    ------
    DatasetLoadError
        Raised when seed file cannot be read or has no usable words.
    """

    try:
        lines = Path(seed_words_path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DatasetLoadError(f"Failed to read seed words: {exc}") from exc

    normalized = {normalize_word(line) for line in lines if normalize_word(line)}
    if len(normalized) == 0:
        raise DatasetLoadError("Seed word list is empty after normalization")

    return normalized

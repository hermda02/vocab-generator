"""Vocabulary dataset loading utilities."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class DatasetLoadError(Exception):
    """Raised when vocabulary dataset loading or validation fails."""


@dataclass(frozen=True)
class VocabularyEntry:
    """Single bilingual vocabulary entry.

    Parameters
    ----------
    word_id : str
        Stable unique identifier of the vocabulary entry.
    norwegian_word : str
        Norwegian word.
    english_word : str
        English equivalent.
    norwegian_definition : str
        Definition in Norwegian.
    english_definition : str
        Definition in English.
    """

    word_id: str
    norwegian_word: str
    english_word: str
    norwegian_definition: str
    english_definition: str


def load_dataset(dataset_path: str) -> list[VocabularyEntry]:
    """Load and validate the bundled vocabulary dataset.

    Parameters
    ----------
    dataset_path : str
        Filesystem path to a JSON dataset file.

    Returns
    -------
    list[VocabularyEntry]
        Validated dataset entries.

    Raises
    ------
    DatasetLoadError
        Raised when the file cannot be read or fails schema validation.
    """

    try:
        raw_payload = Path(dataset_path).read_text(encoding="utf-8")
        parsed_payload = json.loads(raw_payload)
    except (OSError, json.JSONDecodeError) as exc:
        raise DatasetLoadError(f"Failed to read dataset: {exc}") from exc

    if not isinstance(parsed_payload, list) or len(parsed_payload) == 0:
        raise DatasetLoadError("Dataset must be a non-empty JSON array")

    entries: list[VocabularyEntry] = []
    for index, item in enumerate(parsed_payload):
        if not isinstance(item, dict):
            raise DatasetLoadError(f"Entry {index} must be a JSON object")

        required_fields = (
            "word_id",
            "norwegian_word",
            "english_word",
            "norwegian_definition",
            "english_definition",
        )
        for field_name in required_fields:
            value = item.get(field_name)
            if not isinstance(value, str) or value.strip() == "":
                raise DatasetLoadError(
                    f"Entry {index} field {field_name} must be a non-empty string"
                )

        entries.append(
            VocabularyEntry(
                word_id=item["word_id"],
                norwegian_word=item["norwegian_word"],
                english_word=item["english_word"],
                norwegian_definition=item["norwegian_definition"],
                english_definition=item["english_definition"],
            )
        )

    if len({entry.word_id for entry in entries}) != len(entries):
        raise DatasetLoadError("Dataset contains duplicate word_id values")

    return entries

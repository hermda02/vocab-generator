"""Build a larger production vocabulary dataset from Kaikki JSONL exports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen


SOURCE_URL = (
    "https://kaikki.org/dictionary/Norwegian%20Bokm%C3%A5l/"
    "kaikki.org-dictionary-NorwegianBokm%C3%A5l.jsonl"
)
OUTPUT_PATH = Path("data/vocabulary.json")
METADATA_PATH = Path("data/vocabulary-source.json")

ALLOWED_POS = {"noun", "verb", "adj", "adv"}
WORD_PATTERN = re.compile(r"^[a-zA-ZæøåÆØÅ-]{2,}$")
SKIP_GLOSS_PREFIXES = (
    "alternative form of",
    "definite singular of",
    "indefinite plural of",
    "definite plural of",
    "past tense of",
    "present tense of",
    "present participle of",
    "past participle of",
    "comparative of",
    "superlative of",
    "plural of",
    "imperative of",
    "inflection of",
    "subjunctive of",
    "genitive of",
    "attributive of",
    "neuter of",
    "feminine of",
    "masculine of",
    "abbreviation of",
)


def clean_text(value: str) -> str:
    """Normalize whitespace and trim punctuation noise.

    Parameters
    ----------
    value : str
        Raw text candidate.

    Returns
    -------
    str
        Cleaned text suitable for output fields.
    """

    text = re.sub(r"\s+", " ", value).strip()
    return text.strip("-:;,. ")


def pick_gloss(entry: dict[str, object]) -> str | None:
    """Extract the best available English gloss from sense list.

    Parameters
    ----------
    entry : dict[str, object]
        Raw JSONL entry.

    Returns
    -------
    str | None
        Selected gloss if available.
    """

    senses = entry.get("senses")
    if not isinstance(senses, list):
        return None

    for sense in senses:
        if not isinstance(sense, dict):
            continue
        glosses = sense.get("glosses") or sense.get("raw_glosses")
        if not isinstance(glosses, list):
            continue
        for gloss in glosses:
            if not isinstance(gloss, str):
                continue
            cleaned = clean_text(gloss)
            if cleaned:
                return cleaned
    return None


def derive_english_headword(gloss: str) -> str:
    """Derive a compact English equivalent from a gloss.

    Parameters
    ----------
    gloss : str
        English gloss text.

    Returns
    -------
    str
        Compact headword-like equivalent.
    """

    head = gloss.strip()
    head = re.sub(r"^to\s+", "", head, flags=re.IGNORECASE)
    head = re.sub(r"^(?:a|an|the)\s+", "", head, flags=re.IGNORECASE)
    while head.startswith("("):
        head = re.sub(r"^\([^)]*\)\s*", "", head).strip()
    head = re.split(r"\s*\([^)]*\)", head, maxsplit=1)[0].strip()
    head = re.split(r"\s+or\s+", head, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    head = re.split(r"[;,:]", head, maxsplit=1)[0].strip()
    head = clean_text(head)
    words = head.split()
    if len(words) > 4:
        words = words[:4]
    reduced = " ".join(words)
    return reduced or gloss


def is_usable_gloss(gloss: str) -> bool:
    """Return whether a gloss should be kept as lexical meaning.

    Parameters
    ----------
    gloss : str
        Candidate gloss.

    Returns
    -------
    bool
        ``True`` for glosses that appear to be semantic definitions.
    """

    lowered = gloss.lower()
    return not lowered.startswith(SKIP_GLOSS_PREFIXES)


def build_dataset(max_entries: int) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Build normalized vocabulary dataset from Kaikki stream.

    Parameters
    ----------
    max_entries : int
        Maximum number of entries to keep.

    Returns
    -------
    tuple[list[dict[str, str]], dict[str, object]]
        Dataset entries and metadata payload.
    """

    accepted: list[dict[str, str]] = []
    seen_words: set[str] = set()
    scanned = 0

    with urlopen(SOURCE_URL, timeout=120) as response:
        for raw_line in response:
            scanned += 1
            entry = json.loads(raw_line)

            word = entry.get("word")
            pos = entry.get("pos")
            if not isinstance(word, str) or not isinstance(pos, str):
                continue
            if pos not in ALLOWED_POS:
                continue
            if not WORD_PATTERN.match(word):
                continue
            if not word[0].islower():
                continue
            if word in seen_words:
                continue

            gloss = pick_gloss(entry)
            if gloss is None:
                continue
            if not is_usable_gloss(gloss):
                continue
            english_word = derive_english_headword(gloss)
            if not english_word:
                continue

            word_id = "nb-" + hashlib.sha1(f"{word}|{gloss}".encode("utf-8")).hexdigest()[:12]
            accepted.append(
                {
                    "word_id": word_id,
                    "norwegian_word": word,
                    "english_word": english_word,
                    "norwegian_definition": gloss,
                    "english_definition": gloss,
                }
            )
            seen_words.add(word)

            if len(accepted) >= max_entries:
                break

    metadata = {
        "source": "Kaikki / Wiktextract (Norwegian Bokmal)",
        "source_url": SOURCE_URL,
        "license_note": "Derived from Wiktionary-extracted data; verify attribution and licensing requirements.",
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "entries_scanned": scanned,
        "entries_written": len(accepted),
        "filters": {
            "allowed_pos": sorted(ALLOWED_POS),
            "one_entry_per_word": True,
            "max_entries": max_entries,
        },
    }
    return accepted, metadata


def main() -> None:
    """Build and write normalized vocabulary dataset and metadata."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-entries", type=int, default=20000)
    args = parser.parse_args()

    dataset, metadata = build_dataset(max_entries=args.max_entries)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    METADATA_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(dataset)} entries to {OUTPUT_PATH}")
    print(f"wrote metadata to {METADATA_PATH}")


if __name__ == "__main__":
    main()

"""Integration tests for Glance integration asset presence and wiring."""

from __future__ import annotations

from pathlib import Path


def test_glance_assets_reference_required_env_vars() -> None:
    """Reference both internal and browser API URLs in Glance assets."""

    glance_root = Path("deploy/glance")
    root_config = (glance_root / "glance.yml").read_text(encoding="utf-8")
    page_config = (glance_root / "pages/vocabulary.yml").read_text(encoding="utf-8")

    assert "pages:" in root_config
    assert "VOCAB_API_INTERNAL_URL" in page_config
    assert "VOCAB_API_BROWSER_URL" in page_config


def test_glance_page_wires_display_and_refresh_paths() -> None:
    """Wire GET display and POST refresh flows in the page config."""

    page_config = Path("deploy/glance/pages/vocabulary.yml").read_text(encoding="utf-8")

    assert "url: ${VOCAB_API_INTERNAL_URL}/word" in page_config
    assert 'action="${VOCAB_API_BROWSER_URL}/word/new"' in page_config
    assert "Generate New Word" in page_config
    assert "url: ${VOCAB_API_INTERNAL_URL}/health" in page_config

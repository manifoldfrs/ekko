"""Basic tests for ekko.ingest.loader."""

from pathlib import Path

import pytest

from src.ingest import loader
from src.ingest.loader import (
    extract_text_from_pdf,
    extract_text_from_url,
    extract_triples,
)

SAMPLE_PDF = Path(__file__).parent / "fixtures" / "sample.pdf"
SAMPLE_URL = "https://example.com"  # fast dummy; trafilatura handles fetch


@pytest.mark.skipif(not SAMPLE_PDF.exists(), reason="Sample PDF not committed yet")
def test_pdf_extraction():
    text = extract_text_from_pdf(SAMPLE_PDF)
    assert len(text) > 20


def test_url_extraction(monkeypatch):
    """Mock remote fetch to avoid network in CI."""

    monkeypatch.setattr(loader.trafilatura, "fetch_url", lambda url: "<p>Hello</p>")
    monkeypatch.setattr(loader.trafilatura, "extract", lambda html, **_: "Hello world")

    text = extract_text_from_url(SAMPLE_URL)
    assert text == "Hello world"


def test_triple_extraction():
    triples = extract_triples("Barack Obama met Angela Merkel in Berlin.")
    assert ("Barack Obama", "related_to", "Angela Merkel") in triples

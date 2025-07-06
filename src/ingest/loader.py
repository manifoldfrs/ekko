from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pdfminer.high_level
import spacy
import trafilatura

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
INTERIM_DIR.mkdir(parents=True, exist_ok=True)

# spaCy model (lazy-loaded to keep import time low for CLI tooling & tests)
_NLP = None


def _get_nlp():
    global _NLP  # noqa: PLW0603
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def extract_text_from_pdf(path: str | Path) -> str:
    """Return text content from a PDF file."""
    return pdfminer.high_level.extract_text(str(path)).strip()


def extract_text_from_url(url: str) -> str:
    """Fetch and extract article text from a URL (HTML)."""
    html = trafilatura.fetch_url(url)
    if html is None:
        raise ValueError(f"Unable to fetch URL: {url}")
    text = trafilatura.extract(html, include_comments=False, include_tables=False)
    if not text:
        raise ValueError(f"Extraction produced empty text for {url}")
    return text.strip()


EntityTriple = Tuple[str, str, str]


def extract_triples(text: str) -> List[EntityTriple]:
    """
    Naive triple extractor: take consecutive named entities
    and assume pattern (SUBJ, "related_to", OBJ).
    """
    doc = _get_nlp()(text)
    ents = [ent.text for ent in doc.ents if ent.label_ in {"PERSON", "ORG", "GPE"}]
    triples: List[EntityTriple] = []
    for i in range(len(ents) - 1):
        triples.append((ents[i], "related_to", ents[i + 1]))
    return triples


# Orchestrator
def ingest_document(source: str, source_type: str) -> Path:
    """
    Ingest a single document and persist JSONL line with keys:
    {id, source, source_type, text, triples, timestamp}

    Returns path of the JSONL file written.
    """
    if source_type.lower() == "pdf":
        text = extract_text_from_pdf(source)
    elif source_type.lower() in {"url", "web"}:
        text = extract_text_from_url(source)
    else:
        raise ValueError("source_type must be 'pdf' or 'url'")

    triples = extract_triples(text)
    record = {
        "id": os.path.basename(source),
        "source": source,
        "source_type": source_type,
        "text": text,
        "triples": triples,
        "timestamp": datetime.utcnow().isoformat(),
    }

    out_path = INTERIM_DIR / "ingested.jsonl"
    with out_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")

    return out_path

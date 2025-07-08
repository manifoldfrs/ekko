import os

import pytest

pytest.importorskip("src.rag.synthesizer")

from src.rag.synthesizer import generate_answer

TRIPLES = [("Alice", "RELATED_TO", "Bob"), ("Bob", "RELATED_TO", "Charlie")]


def test_generate_answer_stub(monkeypatch):
    # Make sure stub path is taken (no API call)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    out = generate_answer("Who is Bob related to?", TRIPLES)
    assert "[T1]" in out["answer"] and "[T2]" in out["answer"]
    assert "Alice --RELATED_TO-> Bob" in out["prompt"]

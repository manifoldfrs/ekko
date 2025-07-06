import os

import pytest
from py2neo import Graph

pytest.importorskip("py2neo")

from src.graph.builder import _neo4j_graph, build_graph  # noqa: E402


def _db_available() -> bool:
    try:
        _neo4j_graph().run("RETURN 1").evaluate()
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(
    not _db_available(), reason="Neo4j instance not reachable at test time"
)


def test_build_graph(tmp_path, monkeypatch):
    jsonl = tmp_path / "sample.jsonl"
    jsonl.write_text(
        '{"id":"doc1","text":"Alice met Bob.","triples":[["Alice","related_to","Bob"]]}'
    )

    build_graph(jsonl_path=jsonl, schema_first=False)

    g = _neo4j_graph()
    assert g.nodes.match("Entity", name="Alice").first() is not None
    assert g.nodes.match("Entity", name="Bob").first() is not None

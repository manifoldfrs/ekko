import pytest
from numpy import isclose

from src.rag.retriever import _graph, rerank_dense, retrieve_graph

pytest.importorskip("sentence_transformers")
pytest.importorskip("py2neo")


def _db_available() -> bool:
    try:
        _graph().run("RETURN 1").evaluate()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _db_available(), reason="Neo4j instance not reachable"
)


def test_retrieve_and_rerank(tmp_path, monkeypatch):
    """
    Insert two entities manually, then query.
    """
    g = _graph()
    g.run("MATCH (n) DETACH DELETE n")  # clean slate

    g.run(
        """
        MERGE (a:Entity {name:'Alice'})
        MERGE (b:Entity {name:'Bob'})
        MERGE (a)-[:RELATED_TO]->(b)
        """
    )

    triples = retrieve_graph("Alice", k=1)
    assert ("Alice", "RELATED_TO", "Bob") in triples

    top = rerank_dense(triples, "Alice related Bob", top_k=1)
    assert top[0] == ("Alice", "RELATED_TO", "Bob")

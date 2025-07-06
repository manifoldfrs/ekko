"""
------------------

Phase 3 hybrid retrieval:

1. Retrieve a k-hop sub-graph around entities matching the query.
2. Convert triples to text and rerank with a sentence-transformers encoder.

Environment variables
---------------------
NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD - same as builder.py
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import List, Sequence, Tuple

import numpy as np
from py2neo import Graph
from sentence_transformers import SentenceTransformer

Triple = Tuple[str, str, str]


@lru_cache
def _graph() -> Graph:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return Graph(uri, auth=(user, password))


# Dense encoder (lazy)
@lru_cache
def _encoder() -> SentenceTransformer:
    # Small 384-dim encoder; downloads on first use
    return SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_graph(query: str, k: int = 2, limit: int = 50) -> List[Triple]:
    """
    Return unique triples within *k* hops of any entity whose name contains *query*.
    """
    g = _graph()

    # 1. seed entities
    seed_res = g.run(
        """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($q)
        RETURN DISTINCT e.name AS name
        LIMIT 15
        """,
        q=query,
    )
    seeds = [row["name"] for row in seed_res]
    if not seeds:
        return []

    triples: set[Triple] = set()

    # 2. variable-length expansion
    for name in seeds:
        res = g.run(
            f"""
            MATCH p=(e:Entity {{name:$name}})-[:RELATED_TO*1..{k}]-(o:Entity)
            WITH relationships(p) AS rels, nodes(p) AS nodes
            UNWIND range(0, size(rels)-1) AS idx
            RETURN nodes[idx].name AS s, type(rels[idx]) AS p, nodes[idx+1].name AS o
            LIMIT $limit
            """,
            name=name,
            limit=limit,
        )
        triples.update((row["s"], row["p"], row["o"]) for row in res)

    return list(triples)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def rerank_dense(
    triples: Sequence[Triple], query: str, top_k: int = 10
) -> List[Triple]:
    """
    Rerank triples by cosine similarity between dense embeddings of
    *"<subj> <pred> <obj>"* and *query*.
    """
    if not triples:
        return []

    enc = _encoder()
    query_vec = enc.encode(query)

    scored: List[Tuple[float, Triple]] = []
    for t in triples:
        text = " ".join(t)
        vec = enc.encode(text)
        scored.append((_cosine(query_vec, vec), t))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [t for _, t in scored[:top_k]]

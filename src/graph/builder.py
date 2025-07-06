"""Ekko graph.builder

Run ``python -m graph.builder`` after Phase 1 ingestion to populate Neo4j.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from py2neo import Graph, Node, Relationship

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INTERIM_JSONL = PROJECT_ROOT / "data" / "interim" / "ingested.jsonl"
SCHEMA_FILE = Path(__file__).with_name("schema.cypher")


def _neo4j_graph() -> Graph:
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    return Graph(uri, auth=(user, password))


def load_schema(graph: Graph, schema_path: Path = SCHEMA_FILE) -> None:
    """Execute schema.cypher (idempotent thanks to IF NOT EXISTS)."""
    cypher = schema_path.read_text(encoding="utf-8")
    # split on semicolon that ends Cypher statements
    for stmt in filter(None, (s.strip() for s in cypher.split(";"))):
        graph.run(stmt)


def _merge_document(tx, doc_id: str, text: str):
    tx.run(
        "MERGE (d:Document {id:$id}) " "ON CREATE SET d.text=$text",
        id=doc_id,
        text=text,
    )


def _merge_entity(tx, name: str):
    tx.run("MERGE (:Entity {name:$name})", name=name)


def _merge_relationships(tx, doc_id: str, triples: List[Tuple[str, str, str]]):
    for subj, _pred, obj in triples:
        tx.run(
            """
            MATCH (d:Document {id:$doc_id})
            MERGE (s:Entity {name:$subj})
            MERGE (o:Entity {name:$obj})
            MERGE (s)-[:RELATED_TO]->(o)
            MERGE (d)-[:MENTIONS]->(s)
            MERGE (d)-[:MENTIONS]->(o)
            """,
            doc_id=doc_id,
            subj=subj,
            obj=obj,
        )


def build_graph(
    jsonl_path: Path | str = INTERIM_JSONL,
    schema_first: bool = True,
) -> None:
    """Populate Neo4j with nodes/edges from a triples JSONL dump."""
    jsonl_path = Path(jsonl_path)
    if not jsonl_path.exists():
        raise FileNotFoundError(jsonl_path)

    graph = _neo4j_graph()
    if schema_first:
        load_schema(graph)

    with graph.begin() as tx:
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            rec: Dict[str, Any] = json.loads(line)
            doc_id = rec["id"]
            text = rec.get("text", "")
            triples = rec.get("triples", [])
            _merge_document(tx, doc_id, text)
            _merge_relationships(tx, doc_id, triples)


# CLI
def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Build Neo4j knowledge graph")
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=INTERIM_JSONL,
        help="Path to ingested.jsonl (default: %(default)s)",
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Do not run schema.cypher before ingest",
    )
    args = parser.parse_args()

    build_graph(args.jsonl, schema_first=not args.skip_schema)
    print("✅ Knowledge graph loaded.")


if __name__ == "__main__":
    _cli()

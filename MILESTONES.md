# Ekko - Implementation Milestones

> **Target duration:** 7 calendar days (before Delphi intro interview)

| Phase                     | Day(s) | Goal                           | Key Deliverables                                                                        |
| ------------------------- | ------ | ------------------------------ | --------------------------------------------------------------------------------------- |
| **0. Bootstrap**          | 0      | Local dev ready                | ✅ Repo scaffold<br>✅ Virtualenv + `requirements.txt`<br>✅ Neo4j docker-compose       |
| **1. Ingestion ETL**      | 1      | Parse docs -> triples          | • `ingest/loader.py` (PDF, web)<br>• Unit tests covering 3 doc types                    |
| **2. Knowledge Graph**    | 2      | Neo4j schema + population      | • `graph/builder.py`<br>• Cypher schema file (`schema.cypher`)<br>• 1k nodes demo graph |
| **3. Hybrid Retrieval**   | 3-4    | Graph walk + ANN rerank        | • `retriever.py` (Cypher -> dense vectors)<br>• Recall@5 vs. plain ANN notebook         |
| **4. Answer Synthesis**   | 4      | CoT prompt with citations      | • `synthesizer.py`<br>• Example JSON response with node-ids                             |
| **5. API & UI**           | 5      | FastAPI chat + simple React UI | • `/chat` and `/search` endpoints<br>• Front-end chat box (streaming)                   |
| **6. Voice Layer (opt.)** | 6      | Whisper + ElevenLabs           | • `/voice-chat` endpoint<br>• Latency <1.5 s round-trip                                 |
| **7. Polish & Demo**      | 7      | QA, README GIF, Loom           | • End-to-end demo script<br>• Loom recording<br>• Post-mortem notes                     |

---

## Detailed Checklist

### Phase 0 - Bootstrap

- [x] Clone template & initialise Git
- [x] `make dev` spins up Neo4j container
- [x] Pre-commit hooks (black, isort, ruff)

### Phase 1 - Ingestion ETL

- [x] PDF -> text via `pdfminer.six`
- [x] Web article via `trafilatura`
- [x] Triple extraction using spaCy NER + custom patterns
- [x] Write to `data/interim/*.jsonl`

### Phase 2 - Knowledge Graph

- [x] Define node labels: `:Entity`, `:Document`
- [x] Relationship types: `MENTIONS`, `SIMILAR_TO`
- [x] Bulk load with `neo4j-admin import` or transactional Cypher
- [x] Validate graph size & basic queries

### Phase 3 - Hybrid Retrieval

- [x] `retrieve_graph(query)` -> k-hop sub-graph
- [x] `rerank_dense(sub_graph, query)` using sentence-transformers
- [x] Metrics notebook (`notebooks/retrieval_eval.ipynb`)

### Phase 4 - Answer Synthesis

- [x] CoT prompt template in `prompts/`
- [x] Provenance: cite `node.id` in output
- [x] Unit test: answer contains >= 1 citation

### Phase 5 - API & UI

- [x] FastAPI server with streaming SSE
- [ ] React/Vite front-end with chat bubble
- [x] Dockerfile for full-stack deployment

### Phase 6 - Voice (Optional)

- [ ] Whisper real-time transcription
- [ ] ElevenLabs TTS callback
- [ ] WebSocket endpoint for duplex audio

### Phase 7 - Polish & Demo

- [ ] Lighthouse audit (front-end)
- [ ] Record Loom: <2 min walkthrough
- [ ] Update README badges & GIF

---

## Acceptance Criteria

1. **Correctness** - Answers reference real nodes (click opens Neo4j Browser).
2. **Latency** - < 800 ms median (text), < 1.5 s (voice).
3. **Reproducibility** - `make demo` builds graph and serves UI.
4. **Clarity** - Code passes `black`, `isort`, `ruff` and 90 %+ unit test coverage on critical paths.

Happy shipping! 🚀

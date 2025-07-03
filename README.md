# Ekko

> **One-click personal knowledge‑graph chat**
>
> A minimal open‑source prototype that ingests your own corpus (PDFs, YouTube transcripts, tweets), auto‑constructs a heterogeneous knowledge graph, and serves a chat endpoint answering questions by walking the graph + neural rerank. Optional voice front‑end is a cherry on top.

---

## 🚀 Features

- **Heterogeneous Knowledge Graph**: Extract entities & relations, store as nodes & edges in Neo4j
- **Hybrid Retrieval**:

  1. **Graph Walk**: Pull k‑hop neighborhood via Cypher
  2. **Neural Rerank**: Embed triples and rerank by cosine similarity

- **Answer Synthesis**: Chain‑of‑thought prompts with provenance citations
- **Modular Voice UI** (optional): Whisper streaming + ElevenLabs TTS
- **Evaluation Harness**: Benchmarks vs. plain RAG (latency & QA accuracy)

---

## 🛠️ Tech Stack

| Layer            | Tech                                    |
| ---------------- | --------------------------------------- |
| **Backend**      | Python · FastAPI · Uvicorn              |
| **Graph DB**     | Neo4j · py2neo                          |
| **ML**           | PyTorch · DGL · PyG · Transformers      |
| **NLP**          | spaCy · Hugging Face                    |
| **Frontend**     | Node.js · TypeScript · React · Vite     |
| **Voice (opt.)** | OpenAI Whisper · ElevenLabs TTS         |
| **Dev Tools**    | virtualenv · black · isort · pre-commit |

---

## 📋 Prerequisites

- **Python** ≥ 3.10
- **Node.js** ≥ 18.x + npm/Yarn
- **Neo4j** Community or Enterprise (v4.x or v5.x)
- **Docker** (optional for local Neo4j)

---

## ⚙️ Installation & Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ekko.git
cd ekko

# 2. Python environment
python3 -m virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend dependencies
cd frontend
npm install
cd ..

# 4. Configure Neo4j
#   - Copy .env.example → .env and set NEO4J_URI, NEO4J_USER, NEO4J_PASS

# 5. Run backend + frontend
# In one shell:
uvicorn backend.app.main:app --reload
# In another shell:
cd frontend && npm run dev
```

---

## 📂 Project Structure

```
ekko/
├── ekko/          # Python package
│   ├── ingest/    # PDF & web loaders
│   ├── graph/     # KG construction & queries
│   ├── vector/    # Embedding + ANN index
│   ├── rag/       # Retrieval orchestration
│   ├── api/       # FastAPI endpoints
│   └── utils/
├── tests/
├── requirements.txt
├── .cursorignore
└── README.md

```

---

## 🧪 Development Guidelines

- **Formatting**: `black . && isort .`
- **Pre-commit**: Ensure hooks are installed via `pre-commit install`
- **Testing**: `pytest --cov=backend`

---

## 🎤 Optional Voice Integration

1. Enable Whisper streaming in `backend/app/voice.py`
2. Install ElevenLabs credentials in `.env`
3. Use `/voice-chat` endpoint in frontend

---

## 🎯 Next Steps & Roadmap

- ✅ Graph ETL & schema evolution
- ✅ Hybrid retrieval pipeline
- ✅ Answer synthesis with provenance
- 🔲 Voice UI polish & latency tuning
- 🔲 Graph contrastive pre-training

---

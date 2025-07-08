from __future__ import annotations

from typing import AsyncGenerator, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from src.api.schemas import ChatRequest, SearchResponse, Triple
from src.rag import generate_answer, rerank_dense, retrieve_graph

app = FastAPI(
    title="Ekko API",
    description="Personal knowledge-graph chat backend",
    version="0.1.0",
)


# Utility generators
def _answer_stream(message: str) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events (SSE) chunks for the chat answer.
    Currently naive single-chunk; easy to extend to token streaming later.
    """
    triples: List[Triple] = retrieve_graph(message)
    ranked = rerank_dense(triples, message)
    result = generate_answer(message, ranked)
    # SSE spec: lines beginning with "data:"; blank line terminates the event
    yield f"data: {result['answer']}\n\n"


@app.get("/health")
async def health() -> dict:
    """Simple liveness probe."""
    return {"status": "ok"}


@app.get("/search", response_model=SearchResponse)
async def search(q: str) -> SearchResponse:
    """Lightweight graph search helper (no rerank)."""
    triples = retrieve_graph(q)
    return SearchResponse(triples=triples)


@app.post(
    "/chat",
    response_class=StreamingResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
async def chat(req: ChatRequest) -> StreamingResponse:
    """
    Chat endpoint that streams an answer using Server-Sent Events (SSE).
    The client should listen with `EventSource` / `fetch` streaming.
    """
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return StreamingResponse(
        _answer_stream(req.message),
        media_type="text/event-stream",
    )

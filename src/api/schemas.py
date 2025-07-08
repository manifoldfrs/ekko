from __future__ import annotations

from typing import List, Tuple

from pydantic import BaseModel

Triple = Tuple[str, str, str]


class SearchResponse(BaseModel):
    """Return graph triples for an ad-hoc entity search."""

    triples: List[Triple]


class ChatRequest(BaseModel):
    """Inbound chat message from the user."""

    message: str

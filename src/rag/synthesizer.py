"""
Convert query + triples → natural-language answer with provenance citations.
Falls back to a stub response if OPENAI_API_KEY is not set.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Sequence, Tuple

try:
    import openai  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    openai = None  # noqa: N816  – allow later runtime check

Triple = Tuple[str, str, str]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = PROJECT_ROOT / "prompts" / "answer_cot.txt"


def _load_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _render_prompt(question: str, triples: Sequence[Triple]) -> str:
    tpl = _load_template()
    triples_fmt: List[str] = []
    for idx, (s, p, o) in enumerate(triples, 1):
        triples_fmt.append(f"[T{idx}] {s} —{p}→ {o}")
    return tpl.format(question=question, triples_formatted="\n".join(triples_fmt))


def _call_openai(
    prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.2
) -> str:
    if openai is None or os.getenv("OPENAI_API_KEY") is None:
        # Offline fallback for tests / CI
        return "Stub answer citing facts " + ", ".join(
            f"[T{i+1}]" for i in range(prompt.count("[T"))
        )
    client = openai.OpenAI()
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return chat_completion.choices[0].message.content.strip()


def generate_answer(
    question: str,
    triples: Sequence[Triple],
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> dict:
    """Return dict with 'answer' and 'prompt' fields."""
    prompt = _render_prompt(question, triples)
    answer = _call_openai(prompt, model=model, temperature=temperature)
    return {"answer": answer, "prompt": prompt}

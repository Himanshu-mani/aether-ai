"""LLM-based request route classification."""
import re

from app.agents.prompts import ROUTER_PROMPT

VALID_ROUTES = {"DIRECT", "FILE", "SCRAPE", "GENERATE"}


def normalize_route(raw_decision: str) -> str:
    """Normalize a model response to a supported route, defaulting to DIRECT."""
    candidate = str(raw_decision).strip().upper().strip(chr(34) + chr(39) + " .:")
    if candidate in VALID_ROUTES:
        return candidate
    match = re.search(r"\b(DIRECT|FILE|SCRAPE|GENERATE)\b", candidate)
    return match.group(1) if match else "DIRECT"


async def classify_request(llm, query: str) -> str:
    response = await llm.ainvoke(ROUTER_PROMPT.format(query=query))
    return normalize_route(getattr(response, "content", response))

"""Competitor gap analysis.

Expands your seed topic via Google Suggest (real, free) and extracts a
competitor's prominent terms from their actual page (title, headings, meta),
then finds topics the competitor covers that you don't — with an opportunity
score. Optionally refined by an LLM; works without one.
"""

from __future__ import annotations

import json
import re

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.schemas.competitor import CompetitorGapRequest, CompetitorGapResponse, GapItem
from app.services import seo_data
from app.services.copilot import extract_signals
from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_HEADING_RE = re.compile(r"<h[1-3][^>]*>(.*?)</h[1-3]>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9'-]+")
_STOP = {
    "the", "and", "for", "with", "you", "your", "are", "our", "this", "that",
    "from", "all", "can", "will", "how", "what", "why", "get", "new", "more",
    "best", "top", "use", "using", "into", "out", "about", "page", "home",
    "learn", "read", "click", "here", "his", "her", "they", "their", "has",
}


class CompetitorFetchError(RuntimeError):
    """Raised when the competitor page cannot be fetched."""


async def _fetch(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "DClawSEO-Competitor/1.0"})
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPError as exc:
        raise CompetitorFetchError(f"Could not fetch {url}: {exc}") from exc


def extract_competitor_terms(html: str, limit: int = 30) -> list[str]:
    """Prominent multi-word phrases from title + headings (weighted) and body."""
    s = extract_signals(html)
    prominent = " . ".join(filter(None, [s.title, s.meta_description]))
    headings = " . ".join(_TAG_RE.sub(" ", h) for h in _HEADING_RE.findall(html))
    text = f"{prominent} . {headings}".lower()

    phrases: dict[str, int] = {}
    for chunk in text.split("."):
        words = [w for w in _WORD_RE.findall(chunk) if w not in _STOP and len(w) > 2]
        # unigrams + bigrams as candidate keyword phrases
        for w in words:
            phrases[w] = phrases.get(w, 0) + 1
        for a, b in zip(words, words[1:]):
            phrases[f"{a} {b}"] = phrases.get(f"{a} {b}", 0) + 2  # weight phrases
    ranked = sorted(phrases.items(), key=lambda kv: kv[1], reverse=True)
    return [p for p, _ in ranked[:limit]]


def _tokens(s: str) -> set[str]:
    return {w for w in _WORD_RE.findall(s.lower()) if w not in _STOP and len(w) > 2}


def _gaps(your_keywords: list[str], competitor_terms: list[str]) -> list[GapItem]:
    covered: set[str] = set()
    for kw in your_keywords:
        covered |= _tokens(kw)
    gaps: list[GapItem] = []
    for term in competitor_terms:
        toks = _tokens(term)
        if not toks:
            continue
        overlap = len(toks & covered) / len(toks)
        if overlap < 0.5:  # competitor topic largely uncovered by you
            # opportunity: more specific (multi-word) + fully uncovered = higher
            specificity = min(len(toks), 3) / 3
            opportunity = int(round((1 - overlap) * 70 + specificity * 30))
            gaps.append(GapItem(term=term, opportunity=opportunity))
    gaps.sort(key=lambda g: g.opportunity, reverse=True)
    return gaps


_LLM_SYSTEM = (
    "You are an SEO strategist. Given the user's keywords and a competitor's topics, return "
    "ONLY a JSON array of the top content gaps the user should target, each "
    '{"term": str, "opportunity": int (0-100), "reason": str}.'
)


async def _llm_gaps(
    your_keywords: list[str], competitor_terms: list[str], config: LLMConfig
) -> list[GapItem] | None:
    payload = {"your_keywords": your_keywords[:30], "competitor_topics": competitor_terms}
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_LLM_SYSTEM),
                Message(role="user", content=json.dumps(payload)),
            ],
            config=config,
        )
    except LLMNotConfigured:
        return None
    except LLMError as exc:
        logger.warning("competitor_llm_failed", error=str(exc))
        return None
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    out = [
        GapItem(
            term=str(d["term"]),
            opportunity=int(d.get("opportunity", 50)),
            reason=str(d.get("reason")) if d.get("reason") else None,
        )
        for d in (data if isinstance(data, list) else [])
        if isinstance(d, dict) and d.get("term")
    ]
    return out or None


async def competitor_gap(
    db: AsyncSession, request: CompetitorGapRequest
) -> CompetitorGapResponse:
    provider = seo_data.keyword_provider
    try:
        your_keywords = await provider.expand(request.seed, target=40)
    except seo_data.ProviderUnavailable:
        your_keywords = [request.seed]

    html = await _fetch(request.competitor_url)  # may raise CompetitorFetchError
    competitor_terms = extract_competitor_terms(html)

    cfg = await get_effective_config(db)
    llm_gaps = await _llm_gaps(your_keywords, competitor_terms, cfg)
    if llm_gaps is not None:
        gaps, llm_enriched, note = llm_gaps, True, None
    else:
        gaps = _gaps(your_keywords, competitor_terms)
        llm_enriched = False
        note = (
            "Gaps computed by term overlap (no LLM configured). Configure an LLM provider in "
            "Settings for AI opportunity scoring and reasons."
        )

    return CompetitorGapResponse(
        seed=request.seed,
        competitor_url=request.competitor_url,
        your_keyword_count=len(your_keywords),
        competitor_term_count=len(competitor_terms),
        gaps=gaps[:25],
        llm_enriched=llm_enriched,
        note=note,
    )

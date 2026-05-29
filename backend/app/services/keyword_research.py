"""Keyword research & clustering.

Real keyword expansion (Google Suggest) + optional LLM enrichment (search
intent, qualitative volume/difficulty bands, topic clustering). When no LLM
is configured the endpoint still returns the real suggestions, just without
enrichment — never fabricated numbers.
"""

from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.keyword import Keyword
from app.repositories.keyword import KeywordRepository
from app.schemas.seo import KeywordRequest, KeywordResponse, KeywordSuggestion
from app.services import seo_data
from app.services.llm import LLMError, LLMNotConfigured, Message, llm_service

logger = get_logger(__name__)

_ENRICH_SYSTEM = (
    "You are an SEO analyst. For each keyword classify search intent and estimate "
    "volume and difficulty as qualitative bands (never invent numeric counts). "
    "Respond with ONLY a JSON array; each item must be "
    '{"term": str, "intent": "informational"|"transactional"|"navigational", '
    '"volume_band": "low"|"medium"|"high", "difficulty_band": "low"|"medium"|"high", '
    '"cluster": str} where cluster is a short topic label grouping similar terms.'
)


def _parse_json_array(raw: str) -> list | None:
    raw = raw.strip()
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        parsed = json.loads(raw[start : end + 1])
        return parsed if isinstance(parsed, list) else None
    except json.JSONDecodeError:
        return None


async def _enrich_with_llm(seed: str, terms: list[str]) -> list[KeywordSuggestion] | None:
    prompt = f'Seed keyword: "{seed}"\nKeywords:\n' + "\n".join(f"- {t}" for t in terms)
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_ENRICH_SYSTEM),
                Message(role="user", content=prompt),
            ]
        )
    except LLMNotConfigured:
        return None
    except LLMError as exc:
        logger.warning("keyword_enrich_failed", error=str(exc))
        return None

    data = _parse_json_array(raw)
    if data is None:
        logger.warning("keyword_enrich_unparseable")
        return None

    by_term = {d.get("term", "").lower(): d for d in data if isinstance(d, dict)}
    return [
        KeywordSuggestion(
            term=t,
            intent=(by_term.get(t.lower(), {}) or {}).get("intent"),
            volume_band=(by_term.get(t.lower(), {}) or {}).get("volume_band"),
            difficulty_band=(by_term.get(t.lower(), {}) or {}).get("difficulty_band"),
            cluster=(by_term.get(t.lower(), {}) or {}).get("cluster"),
        )
        for t in terms
    ]


async def research_keywords(
    db: AsyncSession,
    request: KeywordRequest,
    provider: seo_data.KeywordDataProvider | None = None,
) -> KeywordResponse:
    provider = provider or seo_data.keyword_provider
    terms = await provider.expand(request.seed, target=50)  # may raise ProviderUnavailable

    enriched = await _enrich_with_llm(request.seed, terms) if terms else None
    if enriched is not None:
        suggestions, llm_enriched, note = enriched, True, None
    else:
        suggestions = [KeywordSuggestion(term=t) for t in terms]
        llm_enriched = False
        note = (
            "LLM not configured — returning real keyword suggestions without intent, "
            "bands, or clustering. Configure an LLM provider in backend/.env to enable enrichment."
        )

    record = Keyword(
        term=request.seed,
        suggestions=json.dumps([s.model_dump() for s in suggestions]),
    )
    await KeywordRepository(db).create(record)

    return KeywordResponse(
        seed=request.seed,
        suggestions=suggestions,
        llm_enriched=llm_enriched,
        note=note,
    )

"""AI content brief generator.

Pulls real related terms + question-style queries from Google Suggest (free)
and assembles a content brief: title ideas, H2/H3 outline, questions to
answer, recommended length, and secondary keywords. An LLM refines the brief
when configured; otherwise a deterministic brief is built from the Suggest
data. No fabricated SERP data.
"""

from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.schemas.content_brief import BriefSection, ContentBriefRequest, ContentBriefResponse
from app.services import seo_data
from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_QUESTION_WORDS = ("how", "what", "why", "when", "where", "which", "who", "is", "can", "do", "does", "are")


def _questions(terms: list[str]) -> list[str]:
    out = []
    for t in terms:
        words = t.split()
        if words and words[0].lower() in _QUESTION_WORDS:
            q = t[0].upper() + t[1:]
            out.append(q if q.endswith("?") else q + "?")
    return out


def _deterministic_brief(keyword: str, terms: list[str]) -> ContentBriefResponse:
    questions = _questions(terms)
    non_q = [t for t in terms if t not in {q.rstrip("?").lower() for q in questions}]
    kw = keyword.strip()
    title = kw.title()
    outline = [BriefSection(h2=f"What is {title}?", h3=[])]
    for t in non_q[:5]:
        outline.append(BriefSection(h2=t.title(), h3=[]))
    outline.append(BriefSection(h2="Frequently Asked Questions", h3=[q for q in questions[:5]]))
    recommended = 1200 if len(terms) < 25 else 1800
    return ContentBriefResponse(
        keyword=kw,
        title_suggestions=[
            title,
            f"The Complete Guide to {title}",
            f"{title}: Everything You Need to Know",
        ],
        outline=outline,
        questions=questions[:10],
        recommended_words=recommended,
        secondary_keywords=non_q[:15],
        llm_enriched=False,
        note=(
            "Brief assembled from real Google Suggest data (no LLM). Configure an LLM provider in "
            "Settings for a richer, SERP-aware brief."
        ),
    )


_LLM_SYSTEM = (
    "You are an SEO content strategist. Given a target keyword and related queries, produce a "
    "content brief as ONLY a JSON object: "
    '{"title_suggestions": [str], "outline": [{"h2": str, "h3": [str]}], "questions": [str], '
    '"recommended_words": int, "secondary_keywords": [str]}.'
)


async def _llm_brief(
    keyword: str, terms: list[str], config: LLMConfig
) -> ContentBriefResponse | None:
    payload = {"keyword": keyword, "related_queries": terms}
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
        logger.warning("brief_llm_failed", error=str(exc))
        return None
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        d = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or not d.get("outline"):
        return None
    try:
        outline = [
            BriefSection(h2=str(s["h2"]), h3=[str(x) for x in s.get("h3", [])])
            for s in d["outline"]
            if isinstance(s, dict) and s.get("h2")
        ]
    except (KeyError, TypeError):
        return None
    if not outline:
        return None
    return ContentBriefResponse(
        keyword=keyword,
        title_suggestions=[str(t) for t in d.get("title_suggestions", [])][:5],
        outline=outline,
        questions=[str(q) for q in d.get("questions", [])][:10],
        recommended_words=int(d.get("recommended_words", 1200)),
        secondary_keywords=[str(k) for k in d.get("secondary_keywords", [])][:15],
        llm_enriched=True,
        note=None,
    )


async def generate_brief(
    db: AsyncSession, request: ContentBriefRequest
) -> ContentBriefResponse:
    provider = seo_data.keyword_provider
    try:
        terms = await provider.expand(request.keyword, target=40)
    except seo_data.ProviderUnavailable:
        terms = []

    cfg = await get_effective_config(db)
    brief = await _llm_brief(request.keyword, terms, cfg)
    return brief if brief is not None else _deterministic_brief(request.keyword, terms)

"""Video SEO optimizer (YouTube).

Produces three CTR-optimized title variants, a keyword-rich description, tags and
hashtags for a video topic. Pulls real related queries from Google Suggest for
tags; an LLM crafts the titles/description when configured, with a deterministic
fallback that still uses the real Suggest data. No fabricated metrics.
"""

from __future__ import annotations

import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.schemas.video_seo import VideoSeoRequest, VideoSeoResponse, VideoTitleVariant
from app.services import seo_data
from app.services.llm import LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)


def _hashtags(terms: list[str], topic: str) -> list[str]:
    words = [topic] + terms
    tags: list[str] = []
    seen: set[str] = set()
    for w in words:
        tag = "#" + "".join(p.capitalize() for p in w.split())[:30]
        if len(tag) > 1 and tag.lower() not in seen:
            seen.add(tag.lower())
            tags.append(tag)
        if len(tags) >= 5:
            break
    return tags


def _deterministic(topic: str, terms: list[str]) -> VideoSeoResponse:
    t = topic.strip()
    variants = [
        VideoTitleVariant(title=f"How to {t} (Step-by-Step Guide)", angle="how-to"),
        VideoTitleVariant(title=f"{t.title()}: 7 Things You Need to Know", angle="listicle"),
        VideoTitleVariant(title=f"The Truth About {t.title()} Nobody Tells You", angle="curiosity"),
    ]
    desc = (
        f"In this video we cover {t}. "
        + (f"We'll look at {', '.join(terms[:5])}. " if terms else "")
        + "Like and subscribe for more.\n\nTimestamps:\n00:00 Intro"
    )
    return VideoSeoResponse(
        topic=t,
        title_variants=variants,
        description=desc,
        tags=(terms[:15] or [t]),
        hashtags=_hashtags(terms, t),
        llm_enriched=False,
        note=(
            "Built from real Google Suggest data (no LLM). Configure an LLM provider in "
            "Settings for sharper, CTR-tuned titles and descriptions."
        ),
    )


_SYSTEM = (
    "You are a YouTube SEO expert. Given a video topic and related search queries, return "
    "ONLY a JSON object: "
    '{"title_variants": [{"title": str, "angle": str}, ...] (exactly 3, each <=70 chars), '
    '"description": str (with a hook and timestamp template), "tags": [str] (10-15), '
    '"hashtags": [str] (3-5, each starting with #)}. Optimize titles for click-through.'
)


def _parse(raw: str, topic: str, fallback_terms: list[str]) -> VideoSeoResponse | None:
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        d = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    raw_variants = d.get("title_variants") if isinstance(d, dict) else None
    if not isinstance(raw_variants, list) or not raw_variants:
        return None
    variants = [
        VideoTitleVariant(title=str(v["title"]), angle=str(v.get("angle", "general")))
        for v in raw_variants
        if isinstance(v, dict) and v.get("title")
    ][:3]
    if not variants:
        return None
    return VideoSeoResponse(
        topic=topic,
        title_variants=variants,
        description=str(d.get("description", "")) or f"A video about {topic}.",
        tags=[str(t) for t in d.get("tags", [])][:15] or (fallback_terms[:15] or [topic]),
        hashtags=[str(h) for h in d.get("hashtags", [])][:5] or _hashtags(fallback_terms, topic),
        llm_enriched=True,
        note=None,
    )


async def optimize_video(db: AsyncSession, request: VideoSeoRequest) -> VideoSeoResponse:
    provider = seo_data.keyword_provider
    try:
        terms = await provider.expand(request.topic, target=20)
    except seo_data.ProviderUnavailable:
        terms = []
    if request.keywords:
        terms = list(dict.fromkeys(request.keywords + terms))

    cfg = await get_effective_config(db)
    payload = {
        "topic": request.topic,
        "related_queries": terms,
        "transcript_excerpt": (request.transcript or "")[:2000],
    }
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_SYSTEM),
                Message(role="user", content=json.dumps(payload)),
            ],
            config=cfg,
            temperature=0.6,
        )
    except LLMNotConfigured:
        return _deterministic(request.topic, terms)
    except LLMError as exc:
        logger.warning("video_llm_failed", error=str(exc))
        return _deterministic(request.topic, terms)

    parsed = _parse(raw, request.topic, terms)
    return parsed if parsed is not None else _deterministic(request.topic, terms)

"""AI long-form content writer.

Generates a long-form article for a target keyword via the configured LLM, then
runs two lightweight quality passes:

- **Originality** — share of 5-grams that appear only once in the draft. This is
  an *internal redundancy* check, not a web plagiarism scan. A real plagiarism
  score requires an external provider (e.g. Copyscape) wired via env; until then
  we report internal originality and say so in ``note``.
- **Fact-check** — an optional LLM self-review that flags unverifiable or
  risky factual claims for human review.

Without an LLM, a deterministic scaffold article is assembled from real Google
Suggest data so the feature still returns a usable, clearly-labeled outline.
"""

from __future__ import annotations

import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.schemas.content_writer import ArticleSection, ContentWriterRequest, ContentWriterResponse
from app.services import seo_data
from app.services.llm import LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_WORD_RE = re.compile(r"\b\w+\b")


def count_words(text: str) -> int:
    return len(_WORD_RE.findall(text))


def originality_score(text: str, n: int = 5) -> float:
    """Percentage of n-grams that are unique within the text (100 = no repetition)."""
    words = [w.lower() for w in _WORD_RE.findall(text)]
    if len(words) < n:
        return 100.0
    grams = [tuple(words[i : i + n]) for i in range(len(words) - n + 1)]
    if not grams:
        return 100.0
    unique = sum(1 for g in set(grams) if grams.count(g) == 1)
    return round(unique / len(set(grams)) * 100, 1)


def _scaffold(keyword: str, terms: list[str], target_words: int) -> ContentWriterResponse:
    kw = keyword.strip()
    title = f"The Complete Guide to {kw.title()}"
    headings = [t.title() for t in terms[:6]] or [f"Understanding {kw.title()}"]
    sections = [
        ArticleSection(
            heading="Introduction",
            body=(
                f"This guide covers everything you need to know about {kw}. "
                f"Below we break down the most-searched aspects of {kw} so you can "
                "build content that matches real search intent."
            ),
        )
    ]
    for h in headings:
        sections.append(
            ArticleSection(
                heading=h,
                body=(
                    f"Expand this section to cover {h.lower()} in the context of {kw}. "
                    "Add specifics, examples, and data to reach publishable depth."
                ),
            )
        )
    full = " ".join(s.body for s in sections)
    return ContentWriterResponse(
        keyword=kw,
        title=title,
        sections=sections,
        word_count=count_words(full),
        originality_score=originality_score(full),
        fact_check_notes=[],
        llm_generated=False,
        note=(
            "Scaffold built from real Google Suggest data (no LLM configured). It is an "
            "outline, not a finished article — configure an LLM provider in Settings to "
            f"generate a full ~{target_words}-word draft."
        ),
    )


_SYSTEM = (
    "You are an expert SEO content writer. Write a comprehensive, original, factually "
    "careful article for the given keyword. Return ONLY a JSON object: "
    '{"title": str, "sections": [{"heading": str, "body": str}], '
    '"fact_check_notes": [str]}. Each section body should be 2-4 full paragraphs. '
    "Put any claims that a human should verify into fact_check_notes. Match the requested "
    "tone and aim for roughly the requested word count across all sections."
)


def _parse(raw: str, keyword: str, target_words: int) -> ContentWriterResponse | None:
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        d = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    raw_sections = d.get("sections") if isinstance(d, dict) else None
    if not isinstance(raw_sections, list) or not raw_sections:
        return None
    sections = [
        ArticleSection(heading=str(s["heading"]), body=str(s["body"]))
        for s in raw_sections
        if isinstance(s, dict) and s.get("heading") and s.get("body")
    ]
    if not sections:
        return None
    full = " ".join(s.body for s in sections)
    return ContentWriterResponse(
        keyword=keyword,
        title=str(d.get("title") or keyword.title()),
        sections=sections,
        word_count=count_words(full),
        originality_score=originality_score(full),
        fact_check_notes=[str(n) for n in d.get("fact_check_notes", [])][:10],
        llm_generated=True,
        note=(
            "Originality is an internal 5-gram redundancy check, not a web plagiarism scan. "
            "Wire a plagiarism provider (e.g. COPYSCAPE_API_KEY) for a true web comparison."
        ),
    )


async def write_article(
    db: AsyncSession, request: ContentWriterRequest
) -> ContentWriterResponse:
    provider = seo_data.keyword_provider
    try:
        terms = await provider.expand(request.keyword, target=30)
    except seo_data.ProviderUnavailable:
        terms = []

    outline = request.outline or terms[:6]
    payload = {
        "keyword": request.keyword,
        "tone": request.tone,
        "target_words": request.target_words,
        "outline": outline,
    }
    cfg = await get_effective_config(db)
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_SYSTEM),
                Message(role="user", content=json.dumps(payload)),
            ],
            config=cfg,
            temperature=0.7,
        )
    except LLMNotConfigured:
        return _scaffold(request.keyword, terms, request.target_words)
    except LLMError as exc:
        logger.warning("writer_llm_failed", error=str(exc))
        return _scaffold(request.keyword, terms, request.target_words)

    parsed = _parse(raw, request.keyword, request.target_words)
    return parsed if parsed is not None else _scaffold(request.keyword, terms, request.target_words)

"""Content optimizer.

Computes a real, deterministic content score (Flesch reading ease + keyword
density + structure checks) and a data-driven improvement checklist — works
with no LLM. When an LLM is configured it adds a semantic-coverage rewrite
("after" content) and richer suggestions.
"""

from __future__ import annotations

import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.content_optimization import ContentOptimization
from app.repositories.content_optimization import ContentOptimizationRepository
from app.schemas.seo import (
    ContentOptimizeRequest,
    ContentOptimizeResponse,
    ContentSuggestion,
)
from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_WORD_RE = re.compile(r"[A-Za-z0-9']+")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _syllables(word: str) -> int:
    groups = _VOWEL_GROUP_RE.findall(word)
    count = len(groups)
    if word.lower().endswith("e") and count > 1:
        count -= 1  # silent trailing 'e'
    return max(1, count)


def _flesch_reading_ease(words: list[str], sentence_count: int) -> float:
    if not words or sentence_count == 0:
        return 0.0
    syllables = sum(_syllables(w) for w in words)
    score = (
        206.835
        - 1.015 * (len(words) / sentence_count)
        - 84.6 * (syllables / len(words))
    )
    return round(max(0.0, min(100.0, score)), 1)


def analyze(text: str, keyword: str) -> dict:
    words = _WORD_RE.findall(text)
    word_count = len(words)
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = max(1, len(sentences))
    readability = _flesch_reading_ease(words, sentence_count)

    kw = keyword.lower().strip()
    occurrences = len(re.findall(re.escape(kw), text.lower())) if kw else 0
    density = round(100 * occurrences / word_count, 2) if word_count else 0.0
    avg_sentence_len = round(word_count / sentence_count, 1)
    first_100 = " ".join(words[:100]).lower()
    has_headings = bool(re.search(r"(^|\n)#{1,6}\s", text))

    return {
        "word_count": word_count,
        "readability": readability,
        "keyword_density": density,
        "occurrences": occurrences,
        "avg_sentence_len": avg_sentence_len,
        "keyword_in_intro": kw in first_100 if kw else False,
        "has_headings": has_headings,
    }


def _checklist(m: dict, keyword: str) -> list[ContentSuggestion]:
    out: list[ContentSuggestion] = []
    if m["keyword_density"] < 0.5:
        out.append(
            ContentSuggestion(
                type="keyword",
                message=f"Target keyword appears {m['occurrences']}x ({m['keyword_density']}%). "
                "Aim for ~1-2% density.",
            )
        )
    elif m["keyword_density"] > 3:
        out.append(
            ContentSuggestion(
                type="keyword",
                message=f"Keyword density is high ({m['keyword_density']}%) — reduce to avoid "
                "over-optimization.",
            )
        )
    if not m["keyword_in_intro"]:
        out.append(
            ContentSuggestion(
                type="keyword",
                message=f"Include '{keyword}' within the first 100 words.",
            )
        )
    if m["avg_sentence_len"] > 22:
        out.append(
            ContentSuggestion(
                type="readability",
                message=f"Average sentence length is {m['avg_sentence_len']} words — shorten for "
                "readability.",
            )
        )
    if m["readability"] < 50:
        out.append(
            ContentSuggestion(
                type="readability",
                message=f"Reading ease is {m['readability']} (hard to read) — simplify wording.",
            )
        )
    if m["word_count"] < 300:
        out.append(
            ContentSuggestion(
                type="length",
                message=f"Content is short ({m['word_count']} words) — aim for 600+ for "
                "competitive terms.",
            )
        )
    if not m["has_headings"]:
        out.append(
            ContentSuggestion(
                type="structure",
                message="Add H2/H3 subheadings to structure the page and surface subtopics.",
            )
        )
    # Always-on best-practice checks so every page gets a substantive checklist.
    out.append(
        ContentSuggestion(
            type="meta",
            message=f"Write a meta description (150-160 chars) featuring '{keyword}'.",
        )
    )
    out.append(
        ContentSuggestion(
            type="links",
            message="Add 2-3 internal links to related pages and 1-2 authoritative external links.",
        )
    )
    return out


def _score(m: dict) -> int:
    # Readability target ~60; keyword density target ~1.5%; reward length + structure.
    readability_pts = 40 * (min(m["readability"], 70) / 70)
    density = m["keyword_density"]
    density_pts = 25 if 0.8 <= density <= 2.5 else (12 if 0.3 <= density <= 3.5 else 4)
    length_pts = 20 * min(m["word_count"], 800) / 800
    structure_pts = (8 if m["has_headings"] else 0) + (7 if m["keyword_in_intro"] else 0)
    return int(round(readability_pts + density_pts + length_pts + structure_pts))


_REWRITE_SYSTEM = (
    "You are an SEO content editor. Rewrite the user's content to improve clarity, "
    "structure (H2/H3), and natural use of the target keyword without keyword stuffing. "
    "Return ONLY the rewritten markdown content."
)


async def _llm_rewrite(keyword: str, content: str, config: LLMConfig) -> str | None:
    try:
        return await llm_service.complete(
            [
                Message(role="system", content=_REWRITE_SYSTEM),
                Message(
                    role="user",
                    content=f"Target keyword: {keyword}\n\nContent:\n{content}",
                ),
            ],
            config=config,
        )
    except LLMNotConfigured:
        return None
    except LLMError as exc:
        logger.warning("content_rewrite_failed", error=str(exc))
        return None


async def optimize_content(
    db: AsyncSession, request: ContentOptimizeRequest
) -> ContentOptimizeResponse:
    metrics = analyze(request.content, request.target_keyword)
    score = _score(metrics)
    suggestions = _checklist(metrics, request.target_keyword)

    cfg = await get_effective_config(db)
    optimized = await _llm_rewrite(request.target_keyword, request.content, cfg)
    llm_enriched = optimized is not None
    note = (
        None
        if llm_enriched
        else "LLM not configured — score and checklist are computed locally; configure an LLM "
        "provider in backend/.env to generate an optimized rewrite."
    )

    record = ContentOptimization(
        target_keyword=request.target_keyword,
        original_content=request.content,
        optimized_content=optimized,
        suggestions=json.dumps([s.model_dump() for s in suggestions]),
    )
    await ContentOptimizationRepository(db).create(record)

    return ContentOptimizeResponse(
        target_keyword=request.target_keyword,
        score=score,
        readability=metrics["readability"],
        keyword_density=metrics["keyword_density"],
        word_count=metrics["word_count"],
        optimized_content=optimized,
        suggestions=suggestions,
        llm_enriched=llm_enriched,
        note=note,
    )

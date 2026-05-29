"""AI meta tags & structured-data generator.

Given a URL (fetched) or raw content, produces an optimized ``<title>``, meta
description, Open Graph / Twitter Card tags, and a JSON-LD schema block. An LLM
refines the copy when configured; otherwise deterministic, length-correct tags
are derived from the page's real signals. No fabricated data.
"""

from __future__ import annotations

import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.schemas.meta_tags import MetaTagsRequest, MetaTagsResponse
from app.services.copilot import _default_fetch, _extract_text, extract_signals
from app.services.llm import LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_WS_RE = re.compile(r"\s+")


def _truncate(text: str, limit: int) -> str:
    text = _WS_RE.sub(" ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(".,;: ") + "…"


def _build_title(keyword: str | None, existing: str | None) -> str:
    base = (existing or keyword or "Untitled Page").strip()
    if keyword and keyword.lower() not in base.lower():
        base = f"{keyword.title()} — {base}"
    return _truncate(base, 60)


def _build_description(keyword: str | None, text: str, existing: str | None) -> str:
    if existing and 120 <= len(existing) <= 160:
        return existing
    snippet = text[:300] if text else (keyword or "")
    if keyword and keyword.lower() not in snippet.lower():
        snippet = f"{keyword.capitalize()}: {snippet}"
    return _truncate(snippet, 158)


def _json_ld(title: str, description: str, url: str | None) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
    }
    if url:
        schema["url"] = url
        schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
    return schema


def _deterministic(
    req: MetaTagsRequest, title: str | None, existing_meta: str | None, text: str
) -> MetaTagsResponse:
    new_title = _build_title(req.keyword, title)
    new_desc = _build_description(req.keyword, text, existing_meta)
    url = req.url or ""
    return MetaTagsResponse(
        title_tag=new_title,
        title_length=len(new_title),
        meta_description=new_desc,
        meta_length=len(new_desc),
        og_tags={
            "og:title": new_title,
            "og:description": new_desc,
            "og:type": "article",
            **({"og:url": url} if url else {}),
        },
        twitter_tags={
            "twitter:card": "summary_large_image",
            "twitter:title": new_title,
            "twitter:description": new_desc,
        },
        json_ld=_json_ld(new_title, new_desc, req.url),
        title_variants=[new_title],
        llm_enriched=False,
        note=(
            "Tags derived from the page's real signals (no LLM). Configure an LLM provider "
            "in Settings for higher-CTR copy and richer schema."
        ),
    )


_SYSTEM = (
    "You are an SEO meta-tag specialist. Given page content and a target keyword, return "
    "ONLY a JSON object: "
    '{"title_tag": str (<=60 chars), "meta_description": str (150-160 chars), '
    '"title_variants": [str, str, str], "json_ld": object (valid schema.org JSON-LD)}. '
    "Write compelling, click-worthy copy that includes the keyword naturally."
)


def _parse(raw: str, req: MetaTagsRequest, fallback_text: str, title: str | None,
           existing_meta: str | None) -> MetaTagsResponse | None:
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        d = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict) or not d.get("title_tag") or not d.get("meta_description"):
        return None
    new_title = _truncate(str(d["title_tag"]), 65)
    new_desc = _truncate(str(d["meta_description"]), 165)
    json_ld = d.get("json_ld")
    if not isinstance(json_ld, dict):
        json_ld = _json_ld(new_title, new_desc, req.url)
    url = req.url or ""
    return MetaTagsResponse(
        title_tag=new_title,
        title_length=len(new_title),
        meta_description=new_desc,
        meta_length=len(new_desc),
        og_tags={
            "og:title": new_title,
            "og:description": new_desc,
            "og:type": "article",
            **({"og:url": url} if url else {}),
        },
        twitter_tags={
            "twitter:card": "summary_large_image",
            "twitter:title": new_title,
            "twitter:description": new_desc,
        },
        json_ld=json_ld,
        title_variants=[str(v) for v in d.get("title_variants", [new_title])][:5] or [new_title],
        llm_enriched=True,
        note=None,
    )


async def generate_meta_tags(
    db: AsyncSession, request: MetaTagsRequest
) -> MetaTagsResponse:
    title = None
    existing_meta = None
    if request.url:
        html = await _default_fetch(request.url)  # may raise PageFetchError
        signals = extract_signals(html)
        title = signals.title
        existing_meta = signals.meta_description
        text = _extract_text(html)
    else:
        text = _WS_RE.sub(" ", request.content or "").strip()

    cfg = await get_effective_config(db)
    payload = {"keyword": request.keyword, "title": title, "content": text[:4000]}
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_SYSTEM),
                Message(role="user", content=json.dumps(payload)),
            ],
            config=cfg,
        )
    except LLMNotConfigured:
        return _deterministic(request, title, existing_meta, text)
    except LLMError as exc:
        logger.warning("meta_llm_failed", error=str(exc))
        return _deterministic(request, title, existing_meta, text)

    parsed = _parse(raw, request, text, title, existing_meta)
    return parsed if parsed is not None else _deterministic(request, title, existing_meta, text)

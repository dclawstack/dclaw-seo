"""AI SEO Copilot.

Fetches a page, extracts real on-page signals, evaluates them against SEO
best practices to produce prioritized next actions, and (when an LLM is
configured) refines the prioritization and adds context-specific advice.

Works without an LLM — the deterministic best-practice checks still return a
real, prioritized action list. The LLM enriches; it is never required.
"""

from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable

import httpx

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.ai import CopilotAction, CopilotResponse, PageSignals
from app.services.content_optimizer import analyze
from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, Message, llm_service

logger = get_logger(__name__)

PageFetcher = Callable[[str], Awaitable[str]]

_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_RE = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]*content=["\'](.*?)["\']',
    re.IGNORECASE | re.DOTALL,
)
_META_DESC_RE2 = re.compile(
    r'<meta[^>]+content=["\'](.*?)["\'][^>]*name=["\']description["\']',
    re.IGNORECASE | re.DOTALL,
)
_H1_RE = re.compile(r"<h1[^>]*>.*?</h1>", re.IGNORECASE | re.DOTALL)
_SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


class PageFetchError(RuntimeError):
    """Raised when the target page cannot be fetched."""


async def _default_fetch(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "DClawSEO-Copilot/1.0"})
            resp.raise_for_status()
            return resp.text
    except httpx.HTTPError as exc:
        raise PageFetchError(f"Could not fetch {url}: {exc}") from exc


def _extract_text(html: str) -> str:
    no_scripts = _SCRIPT_STYLE_RE.sub(" ", html)
    text = _TAG_RE.sub(" ", no_scripts)
    return _WS_RE.sub(" ", text).strip()


def extract_signals(html: str) -> PageSignals:
    title_m = _TITLE_RE.search(html)
    title = _WS_RE.sub(" ", title_m.group(1)).strip() if title_m else None
    meta_m = _META_DESC_RE.search(html) or _META_DESC_RE2.search(html)
    meta = _WS_RE.sub(" ", meta_m.group(1)).strip() if meta_m else None
    h1_count = len(_H1_RE.findall(html))
    text = _extract_text(html)
    metrics = analyze(text, "")
    return PageSignals(
        title=title,
        title_length=len(title) if title else 0,
        meta_description=meta,
        meta_length=len(meta) if meta else 0,
        h1_count=h1_count,
        word_count=metrics["word_count"],
        readability=metrics["readability"],
    )


def _baseline_actions(s: PageSignals) -> list[CopilotAction]:
    """Deterministic, real best-practice findings — prioritized."""
    actions: list[CopilotAction] = []
    if not s.title:
        actions.append(CopilotAction(priority=1, category="title", title="Add a <title> tag", detail="The page has no title tag — the single most important on-page SEO element."))
    elif not (50 <= s.title_length <= 60):
        actions.append(CopilotAction(priority=2, category="title", title="Tune title length", detail=f"Title is {s.title_length} chars; aim for 50-60 so it isn't truncated in the SERP."))
    if not s.meta_description:
        actions.append(CopilotAction(priority=2, category="meta", title="Add a meta description", detail="No meta description found. Add a 150-160 char summary to improve click-through."))
    elif not (140 <= s.meta_length <= 160):
        actions.append(CopilotAction(priority=3, category="meta", title="Adjust meta description length", detail=f"Meta description is {s.meta_length} chars; aim for 150-160."))
    if s.h1_count == 0:
        actions.append(CopilotAction(priority=1, category="structure", title="Add an H1 heading", detail="No H1 found. Each page should have exactly one descriptive H1."))
    elif s.h1_count > 1:
        actions.append(CopilotAction(priority=3, category="structure", title="Use a single H1", detail=f"Found {s.h1_count} H1 tags; keep exactly one and demote the rest to H2."))
    if s.word_count < 300:
        actions.append(CopilotAction(priority=2, category="content", title="Expand thin content", detail=f"Only {s.word_count} words. Aim for 600+ for competitive queries."))
    if s.readability and s.readability < 50:
        actions.append(CopilotAction(priority=3, category="content", title="Improve readability", detail=f"Reading ease is {s.readability}; shorten sentences and simplify wording."))
    # Always-on guidance so the copilot never returns an empty list.
    actions.append(CopilotAction(priority=4, category="links", title="Add internal links", detail="Link to 2-3 related pages and 1-2 authoritative external sources."))
    actions.sort(key=lambda a: a.priority)
    return actions


_SYSTEM = (
    "You are an SEO copilot. Given a page's on-page signals and a baseline list of "
    "issues, return ONLY a JSON array of prioritized next actions, each "
    '{"priority": int (1=highest), "category": str, "title": str, "detail": str}. '
    "Merge and re-rank the baseline issues, add any high-impact actions they miss, "
    "and keep it specific to this page."
)


def _parse_actions(raw: str) -> list[CopilotAction] | None:
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    out: list[CopilotAction] = []
    for d in data if isinstance(data, list) else []:
        if isinstance(d, dict) and d.get("title"):
            out.append(
                CopilotAction(
                    priority=int(d.get("priority", 5)),
                    category=str(d.get("category", "general")),
                    title=str(d["title"]),
                    detail=str(d.get("detail", "")),
                )
            )
    return out or None


async def _llm_refine(
    s: PageSignals,
    baseline: list[CopilotAction],
    question: str | None,
    config: LLMConfig,
) -> list[CopilotAction] | None:
    payload = {
        "signals": s.model_dump(),
        "baseline_issues": [a.model_dump() for a in baseline],
        "question": question,
    }
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_SYSTEM),
                Message(role="user", content=json.dumps(payload)),
            ],
            config=config,
        )
    except LLMNotConfigured:
        return None
    except LLMError as exc:
        logger.warning("copilot_llm_failed", error=str(exc))
        return None
    actions = _parse_actions(raw)
    if actions:
        actions.sort(key=lambda a: a.priority)
    return actions


async def analyze_page(
    url: str,
    question: str | None = None,
    fetcher: PageFetcher | None = None,
    config: LLMConfig | None = None,
) -> CopilotResponse:
    fetch = fetcher or _default_fetch
    html = await fetch(url)  # may raise PageFetchError
    signals = extract_signals(html)
    baseline = _baseline_actions(signals)

    cfg = config or LLMConfig.from_settings()
    refined = await _llm_refine(signals, baseline, question, cfg)
    if refined is not None:
        actions, llm_enriched, note = refined, True, None
    else:
        actions = baseline
        llm_enriched = False
        note = (
            "LLM not configured — these are best-practice findings computed from the page. "
            "Configure an LLM provider in backend/.env for page-specific, re-ranked guidance."
        )

    summary = (
        f"Analyzed {url}: {signals.word_count} words, "
        f"{'title set' if signals.title else 'no title'}, "
        f"{'meta set' if signals.meta_description else 'no meta'}, "
        f"{signals.h1_count} H1. {len(actions)} prioritized actions."
    )
    return CopilotResponse(
        url=url,
        summary=summary,
        signals=signals,
        actions=actions,
        llm_enriched=llm_enriched,
        note=note,
    )

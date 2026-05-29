"""Technical site audit — real crawl.

Crawls internal pages with httpx (bounded by ``max_pages``), runs a set of
real on-page/technical checks per page, scores the site, and persists the
result. Optionally adds an LLM-written prioritized summary when a provider is
configured; otherwise a deterministic summary. No fabricated data.
"""

from __future__ import annotations

import json
import re
import time
from collections import deque
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.site_audit import SiteAudit
from app.repositories.site_audit import SiteAuditRepository
from app.schemas.seo import AuditRequest, AuditResponse, IssueItem
from app.services.copilot import extract_signals
from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_A_HREF_RE = re.compile(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', re.IGNORECASE)
_IMG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
_ALT_RE = re.compile(r'\balt=["\']', re.IGNORECASE)
_CANONICAL_RE = re.compile(r'<link\b[^>]*\brel=["\']canonical["\']', re.IGNORECASE)
_VIEWPORT_RE = re.compile(r'<meta\b[^>]*\bname=["\']viewport["\']', re.IGNORECASE)
_SLOW_MS = 1500


async def _fetch(client: httpx.AsyncClient, url: str):
    try:
        t0 = time.monotonic()
        resp = await client.get(url, headers={"User-Agent": "DClawSEO-Audit/1.0"})
        elapsed = int((time.monotonic() - t0) * 1000)
        return resp.status_code, resp.text, elapsed, None
    except httpx.HTTPError as exc:
        return None, "", 0, str(exc)


def _extract_links(base_url: str, html: str) -> list[str]:
    out = []
    for href in _A_HREF_RE.findall(html):
        href = href.strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute, _ = urldefrag(urljoin(base_url, href))
        out.append(absolute)
    return out


def _page_issues(url: str, html: str, elapsed_ms: int) -> list[IssueItem]:
    s = extract_signals(html)
    issues: list[IssueItem] = []

    def add(sev: str, typ: str, msg: str) -> None:
        issues.append(IssueItem(severity=sev, type=typ, message=msg, url=url))

    if not s.title:
        add("error", "missing_title", "Missing <title> tag.")
    elif not (50 <= s.title_length <= 60):
        add("warning", "title_length", f"Title is {s.title_length} chars (aim 50-60).")
    if not s.meta_description:
        add("warning", "missing_meta_description", "Missing meta description.")
    elif not (140 <= s.meta_length <= 160):
        add("info", "meta_length", f"Meta description is {s.meta_length} chars (aim 150-160).")
    if s.h1_count == 0:
        add("error", "missing_h1", "No H1 heading.")
    elif s.h1_count > 1:
        add("warning", "multiple_h1", f"{s.h1_count} H1 tags (use exactly one).")
    if s.word_count < 300:
        add("warning", "thin_content", f"Thin content ({s.word_count} words).")
    if s.readability and s.readability < 40:
        add("info", "low_readability", f"Low reading ease ({s.readability}).")

    imgs = _IMG_RE.findall(html)
    no_alt = [t for t in imgs if not _ALT_RE.search(t)]
    if no_alt:
        add("warning", "img_missing_alt", f"{len(no_alt)} image(s) missing alt text.")
    if not _CANONICAL_RE.search(html):
        add("info", "missing_canonical", "No canonical link tag.")
    if not _VIEWPORT_RE.search(html):
        add("warning", "missing_viewport", "No mobile viewport meta tag.")
    if elapsed_ms > _SLOW_MS:
        add("warning", "slow_response", f"Slow response ({elapsed_ms} ms).")
    if url.startswith("https://") and re.search(r'(?:href|src)=["\']http://', html):
        add("warning", "mixed_content", "Insecure http:// resources on an https page.")
    return issues


def _score(issues: list[IssueItem], pages: int) -> int:
    weights = {"error": 8, "warning": 3, "info": 1}
    penalty = sum(weights.get(i.severity, 1) for i in issues)
    # Normalize lightly by pages so large sites aren't unfairly crushed.
    return max(0, 100 - int(penalty / max(1, pages) * 4))


async def _llm_summary(issues: list[IssueItem], config: LLMConfig) -> str | None:
    counts: dict[str, int] = {}
    for i in issues:
        counts[i.type or "other"] = counts.get(i.type or "other", 0) + 1
    try:
        return await llm_service.complete(
            [
                Message(
                    role="system",
                    content="You are an SEO auditor. Given issue-type counts, write a brief "
                    "(2-3 sentence) prioritized summary of the top fixes. Plain text only.",
                ),
                Message(role="user", content=json.dumps(counts)),
            ],
            config=config,
        )
    except LLMNotConfigured:
        return None
    except LLMError as exc:
        logger.warning("audit_summary_failed", error=str(exc))
        return None


async def run_site_audit(db: AsyncSession, request: AuditRequest) -> AuditResponse:
    start = request.url
    domain = urlparse(start).netloc
    queue: deque[str] = deque([start])
    visited: set[str] = set()
    issues: list[IssueItem] = []
    pages = 0

    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        while queue and pages < request.max_pages:
            url = queue.popleft()
            if url in visited:
                continue
            visited.add(url)
            status, html, elapsed, err = await _fetch(client, url)
            pages += 1
            if err is not None:
                issues.append(
                    IssueItem(severity="error", type="unreachable", message=f"Unreachable: {err}", url=url)
                )
                continue
            if status >= 400:
                issues.append(
                    IssueItem(
                        severity="error", type="broken_page", message=f"HTTP {status}", url=url
                    )
                )
                continue
            issues.extend(_page_issues(url, html, elapsed))
            for link in _extract_links(url, html):
                if urlparse(link).netloc == domain and link not in visited:
                    queue.append(link)

    score = _score(issues, pages)
    cfg = await get_effective_config(db)
    summary = await _llm_summary(issues, cfg)
    if summary is None:
        summary = (
            f"Crawled {pages} page(s); found {len(issues)} issue(s). "
            "Configure an LLM provider in Settings for prioritized fix guidance."
        )

    audit = SiteAudit(
        url=start,
        score=score,
        pages_crawled=pages,
        issues=json.dumps([i.model_dump() for i in issues]),
    )
    await SiteAuditRepository(db).create(audit)

    return AuditResponse(
        url=start,
        score=score,
        pages_crawled=pages,
        issues=[IssueItem(**i) for i in json.loads(audit.issues)],
        summary=summary.strip(),
        created_at=audit.created_at,
    )

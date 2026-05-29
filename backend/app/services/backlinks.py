"""Backlink analysis & monitoring.

No free, keyless backlink index exists, so links come from a pluggable
provider (default: none) or are supplied by the user — real data only.
Each link gets a heuristic toxicity score (always), optionally refined by an
LLM. Re-analyzing a target detects new and lost links.
"""

from __future__ import annotations

import ipaddress
import json
import re
from typing import Protocol
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.backlink import Backlink
from app.repositories.backlink import BacklinkRepository
from app.schemas.backlinks import (
    BacklinkAnalyzeRequest,
    BacklinkAnalyzeResponse,
    BacklinkItem,
)
from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config
from app.core.utils import utc_now

logger = get_logger(__name__)

_SPAM_TLDS = {
    "xyz", "top", "loan", "work", "click", "gq", "ml", "cf", "tk",
    "date", "racing", "win", "review", "stream", "bid", "download",
}
_SPAM_ANCHOR_TERMS = (
    "casino", "viagra", "porn", "payday", "loan", "replica", "forex",
    "crypto", "cheap", "buy now", "escort", "betting",
)
_TOXIC_THRESHOLD = 60


class BacklinkProvider(Protocol):
    name: str

    async def fetch(self, target_url: str) -> list[dict]: ...


class NullBacklinkProvider:
    name = "none"

    async def fetch(self, target_url: str) -> list[dict]:  # noqa: ARG002
        return []


backlink_provider: BacklinkProvider = NullBacklinkProvider()


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.split(":")[0])
        return True
    except ValueError:
        return False


def heuristic_toxicity(source_url: str, anchor: str | None) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []
    host = (urlparse(source_url).netloc or "").lower()
    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in _SPAM_TLDS:
        score += 40
        reasons.append(f"spammy TLD .{tld}")
    if host and _is_ip(host):
        score += 30
        reasons.append("IP-address host")
    if host.count(".") >= 4:
        score += 15
        reasons.append("excessive subdomains")
    a = (anchor or "").lower()
    if any(term in a for term in _SPAM_ANCHOR_TERMS):
        score += 35
        reasons.append("commercial/spam anchor text")
    if len(a) > 80:
        score += 10
        reasons.append("very long anchor text")
    if not re.match(r"^https?://", source_url):
        score += 10
        reasons.append("non-standard URL")
    return min(100, score), reasons


_LLM_SYSTEM = (
    "You are a backlink auditor. For each backlink (source_url + anchor), assess SEO "
    "toxicity 0-100 (0 clean, 100 clearly spammy). Respond with ONLY a JSON array of "
    '{"source_url": str, "toxic_score": int, "toxic_reason": str}.'
)


async def _llm_scores(links: list[dict], config: LLMConfig) -> dict[str, dict] | None:
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_LLM_SYSTEM),
                Message(role="user", content=json.dumps(links)),
            ],
            config=config,
        )
    except LLMNotConfigured:
        return None
    except LLMError as exc:
        logger.warning("backlink_llm_failed", error=str(exc))
        return None
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    out = {}
    for d in data if isinstance(data, list) else []:
        if isinstance(d, dict) and d.get("source_url"):
            out[d["source_url"]] = d
    return out or None


def _to_item(b: Backlink) -> BacklinkItem:
    return BacklinkItem(
        source_url=b.source_url,
        anchor_text=b.anchor_text,
        toxic_score=b.toxic_score,
        toxic_reason=b.toxic_reason,
        status=b.status,
        first_seen=b.first_seen,
        last_seen=b.last_seen,
    )


async def analyze_backlinks(
    db: AsyncSession,
    request: BacklinkAnalyzeRequest,
    provider: BacklinkProvider | None = None,
) -> BacklinkAnalyzeResponse:
    provider = provider or backlink_provider
    target = request.target_url

    # Merge user-supplied links with any from a configured provider (deduped by source).
    incoming: dict[str, dict] = {}
    for link in await provider.fetch(target):
        if link.get("source_url"):
            incoming[link["source_url"]] = {"source_url": link["source_url"], "anchor_text": link.get("anchor_text")}
    for link in request.links:
        incoming[link.source_url] = {"source_url": link.source_url, "anchor_text": link.anchor_text}

    cfg = await get_effective_config(db)
    llm = await _llm_scores(list(incoming.values()), cfg) if incoming else None

    repo = BacklinkRepository(db)
    existing = {b.source_url: b for b in await repo.for_target(target)}
    now = utc_now()
    new_count = 0

    for source_url, link in incoming.items():
        h_score, h_reasons = heuristic_toxicity(source_url, link.get("anchor_text"))
        score, reason = h_score, ", ".join(h_reasons) or "no obvious spam signals"
        if llm and source_url in llm:
            ls = llm[source_url]
            if isinstance(ls.get("toxic_score"), int):
                score = ls["toxic_score"]
                reason = str(ls.get("toxic_reason") or reason)

        row = existing.get(source_url)
        if row is None:
            new_count += 1
            db.add(
                Backlink(
                    target_url=target,
                    source_url=source_url,
                    anchor_text=link.get("anchor_text"),
                    toxic_score=score,
                    toxic_reason=reason,
                    status="active",
                )
            )
        else:
            row.anchor_text = link.get("anchor_text")
            row.toxic_score = score
            row.toxic_reason = reason
            row.status = "active"
            row.last_seen = now

    # Links previously stored but absent from this snapshot are now lost.
    lost_count = 0
    for source_url, row in existing.items():
        if source_url not in incoming and row.status != "lost":
            row.status = "lost"
            lost_count += 1

    await db.commit()

    rows = await repo.for_target(target)
    items = [_to_item(b) for b in rows]
    toxic_count = sum(1 for b in rows if (b.toxic_score or 0) >= _TOXIC_THRESHOLD)
    note = None if llm is not None else (
        "Toxicity scored heuristically (no LLM configured). Configure an LLM provider in "
        "Settings for AI-refined scoring; connect a backlink-data provider for automatic discovery."
    )
    return BacklinkAnalyzeResponse(
        target_url=target,
        total=len(rows),
        toxic_count=toxic_count,
        new_count=new_count,
        lost_count=lost_count,
        llm_enriched=llm is not None,
        note=note,
        backlinks=items,
    )


async def list_backlinks(db: AsyncSession, target_url: str) -> BacklinkAnalyzeResponse:
    repo = BacklinkRepository(db)
    rows = await repo.for_target(target_url)
    items = [_to_item(b) for b in rows]
    toxic_count = sum(1 for b in rows if (b.toxic_score or 0) >= _TOXIC_THRESHOLD)
    return BacklinkAnalyzeResponse(
        target_url=target_url,
        total=len(rows),
        toxic_count=toxic_count,
        new_count=0,
        lost_count=sum(1 for b in rows if b.status == "lost"),
        llm_enriched=False,
        note=None,
        backlinks=items,
    )

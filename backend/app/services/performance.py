"""Core Web Vitals / performance monitor.

Uses the Google PageSpeed Insights API (real Lighthouse data, free; set
PAGESPEED_API_KEY for reliable quota). Records each observation for trend
history and derives recommendations. Raises PerfUnavailable on API errors
(e.g. quota/429) — never fabricates metrics.
"""

from __future__ import annotations

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.performance_metric import PerformanceMetric
from app.repositories.performance_metric import PerformanceMetricRepository
from app.schemas.performance import PerformanceRequest, PerformanceResponse, PerfPoint

logger = get_logger(__name__)

PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


class PerfUnavailable(RuntimeError):
    """Raised when PageSpeed Insights cannot return a result."""


def _audit_ms(audits: dict, key: str) -> int | None:
    v = audits.get(key, {}).get("numericValue")
    return int(round(v)) if isinstance(v, (int, float)) else None


def parse_psi(data: dict) -> dict:
    """Extract score + CWV from a PageSpeed Insights response. Raises ValueError."""
    if "error" in data:
        raise ValueError(data["error"].get("message", "PSI error"))
    lh = data.get("lighthouseResult") or {}
    if lh.get("runtimeError"):
        raise ValueError(lh["runtimeError"].get("message", "Lighthouse runtime error"))
    audits = lh.get("audits") or {}
    score = lh.get("categories", {}).get("performance", {}).get("score")
    cls_v = audits.get("cumulative-layout-shift", {}).get("numericValue")
    return {
        "score": int(round(score * 100)) if isinstance(score, (int, float)) else None,
        "lcp_ms": _audit_ms(audits, "largest-contentful-paint"),
        "cls": round(cls_v, 3) if isinstance(cls_v, (int, float)) else None,
        "fcp_ms": _audit_ms(audits, "first-contentful-paint"),
        "tbt_ms": _audit_ms(audits, "total-blocking-time"),
        "si_ms": _audit_ms(audits, "speed-index"),
    }


def _recommendations(m: dict) -> list[str]:
    recs: list[str] = []
    if m["lcp_ms"] and m["lcp_ms"] > 2500:
        recs.append(f"Improve LCP ({m['lcp_ms'] / 1000:.1f}s; target < 2.5s) — optimize the hero image/server response.")
    if m["cls"] is not None and m["cls"] > 0.1:
        recs.append(f"Reduce layout shift (CLS {m['cls']}; target < 0.1) — set size attributes on media.")
    if m["tbt_ms"] and m["tbt_ms"] > 200:
        recs.append(f"Reduce Total Blocking Time ({m['tbt_ms']} ms) — split/defer long JavaScript tasks.")
    if m["fcp_ms"] and m["fcp_ms"] > 1800:
        recs.append(f"Improve First Contentful Paint ({m['fcp_ms'] / 1000:.1f}s) — reduce render-blocking resources.")
    if not recs and m["score"] is not None:
        recs.append("Core Web Vitals look healthy — keep monitoring for regressions.")
    return recs


async def _run_psi(url: str, strategy: str) -> dict:
    params = {"url": url, "strategy": strategy, "category": "performance"}
    if settings.pagespeed_api_key:
        params["key"] = settings.pagespeed_api_key
    try:
        async with httpx.AsyncClient(timeout=70.0) as client:
            resp = await client.get(PSI_URL, params=params)
            data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise PerfUnavailable(f"PageSpeed Insights request failed: {exc}") from exc
    try:
        return parse_psi(data)
    except ValueError as exc:
        raise PerfUnavailable(str(exc)) from exc


async def monitor_performance(
    db: AsyncSession, request: PerformanceRequest
) -> PerformanceResponse:
    strategy = "desktop" if request.strategy == "desktop" else "mobile"
    metrics = await _run_psi(request.url, strategy)  # raises PerfUnavailable

    repo = PerformanceMetricRepository(db)
    await repo.create(
        PerformanceMetric(
            url=request.url,
            strategy=strategy,
            score=metrics["score"],
            lcp_ms=metrics["lcp_ms"],
            cls=metrics["cls"],
            fcp_ms=metrics["fcp_ms"],
            tbt_ms=metrics["tbt_ms"],
            si_ms=metrics["si_ms"],
        )
    )
    rows = await repo.history(request.url)
    history = [
        PerfPoint(fetched_at=r.fetched_at, score=r.score, lcp_ms=r.lcp_ms, cls=r.cls)
        for r in rows
    ]
    return PerformanceResponse(
        url=request.url,
        strategy=strategy,
        recommendations=_recommendations(metrics),
        history=history,
        **metrics,
    )


async def performance_history(db: AsyncSession, url: str) -> PerformanceResponse:
    rows = await PerformanceMetricRepository(db).history(url)
    history = [
        PerfPoint(fetched_at=r.fetched_at, score=r.score, lcp_ms=r.lcp_ms, cls=r.cls)
        for r in rows
    ]
    latest = rows[-1] if rows else None
    return PerformanceResponse(
        url=url,
        strategy=latest.strategy if latest else "mobile",
        score=latest.score if latest else None,
        lcp_ms=latest.lcp_ms if latest else None,
        cls=latest.cls if latest else None,
        fcp_ms=latest.fcp_ms if latest else None,
        tbt_ms=latest.tbt_ms if latest else None,
        si_ms=latest.si_ms if latest else None,
        history=history,
    )

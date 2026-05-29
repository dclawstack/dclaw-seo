import hashlib
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ranking import Ranking
from app.models.site_audit import SiteAudit
from app.repositories.ranking import RankingRepository
from app.repositories.site_audit import SiteAuditRepository
from app.schemas.seo import (
    AuditRequest,
    AuditResponse,
    IssueItem,
    RankDataPoint,
    RankingsTrackRequest,
    RankingsTrackResponse,
)


def _stable_int(seed: str, lo: int, hi: int) -> int:
    """Deterministic, reproducible value in [lo, hi] derived from ``seed``.

    TODO(P1): replace these placeholder estimates with real provider data
    (DataForSEO / SerpApi / Ahrefs) once the data-provider client is wired.
    """
    digest = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return lo + digest % (hi - lo + 1)


async def run_site_audit(db: AsyncSession, request: AuditRequest) -> AuditResponse:
    score = _stable_int(request.url, 55, 98)  # TODO(P1): score from a real crawl
    issues = [
        IssueItem(severity="warning", message="Missing meta description on /about"),
        IssueItem(severity="error", message="Slow LCP (>2.5s) on mobile"),
        IssueItem(severity="info", message="Add structured data for breadcrumbs"),
    ]
    if score > 85:
        issues = [i for i in issues if i.severity != "error"]
    audit = SiteAudit(
        url=request.url,
        score=score,
        issues=json.dumps([i.model_dump() for i in issues]),
    )
    await SiteAuditRepository(db).create(audit)
    stored = [IssueItem(**i) for i in json.loads(audit.issues)]
    return AuditResponse(
        url=audit.url, score=audit.score, issues=stored, created_at=audit.created_at
    )


async def track_rankings(
    db: AsyncSession, request: RankingsTrackRequest
) -> RankingsTrackResponse:
    repo = RankingRepository(db)
    key = f"{request.keyword}|{request.url}"
    observation = Ranking(
        keyword=request.keyword,
        url=request.url,
        position=_stable_int(key, 3, 25),  # TODO(P1): real SERP position check
        competitor_position=_stable_int(f"{key}|comp", 1, 28),
    )
    await repo.create(observation)
    rows = await repo.history(request.keyword, request.url)
    history = [
        RankDataPoint(
            date=r.tracked_at.strftime("%Y-%m-%d"),
            position=r.position,
            competitor_position=r.competitor_position or r.position,
        )
        for r in rows
    ]
    return RankingsTrackResponse(keyword=request.keyword, url=request.url, history=history)

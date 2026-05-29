import hashlib
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.site_audit import SiteAudit
from app.repositories.site_audit import SiteAuditRepository
from app.schemas.seo import (
    AuditRequest,
    AuditResponse,
    IssueItem,
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

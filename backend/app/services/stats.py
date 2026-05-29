"""Dashboard statistics — real aggregates from the database."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.content_optimization import ContentOptimizationRepository
from app.repositories.keyword import KeywordRepository
from app.repositories.ranking import RankingRepository
from app.repositories.site_audit import SiteAuditRepository
from app.schemas.seo import ActivityItem, DashboardStats


async def dashboard_stats(db: AsyncSession) -> DashboardStats:
    audits_repo = SiteAuditRepository(db)
    keywords_repo = KeywordRepository(db)
    content_repo = ContentOptimizationRepository(db)
    rankings_repo = RankingRepository(db)

    recent_audits = await audits_repo.recent(5)
    recent_keywords = await keywords_repo.recent(5)
    recent_content = await content_repo.recent(5)
    recent_rankings = await rankings_repo.recent(5)

    activity: list[ActivityItem] = []
    activity += [ActivityItem(type="audit", label=a.url, at=a.created_at) for a in recent_audits]
    activity += [
        ActivityItem(type="keyword", label=k.term, at=k.created_at) for k in recent_keywords
    ]
    activity += [
        ActivityItem(type="content", label=c.target_keyword, at=c.created_at)
        for c in recent_content
    ]
    activity += [
        ActivityItem(type="ranking", label=f"{r.keyword} @ #{r.position}", at=r.tracked_at)
        for r in recent_rankings
    ]
    activity.sort(key=lambda i: i.at, reverse=True)

    return DashboardStats(
        audits=await audits_repo.count(),
        keywords=await keywords_repo.count(),
        optimizations=await content_repo.count(),
        rank_observations=await rankings_repo.count(),
        latest_audit_score=recent_audits[0].score if recent_audits else None,
        recent=activity[:8],
    )

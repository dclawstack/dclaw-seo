import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.seo import (
    AuditRequest,
    AuditResponse,
    IssueItem,
    KeywordRequest,
    KeywordResponse,
    KeywordSuggestion,
    ContentOptimizeRequest,
    ContentOptimizeResponse,
    ContentSuggestion,
    RankingsTrackRequest,
    RankingsTrackResponse,
    RankDataPoint,
)
from app.models.site_audit import SiteAudit
from app.models.keyword import Keyword
from app.models.content_optimization import ContentOptimization
from app.models.ranking import Ranking
from app.repositories.content_optimization import ContentOptimizationRepository
from app.repositories.keyword import KeywordRepository
from app.repositories.ranking import RankingRepository
from app.repositories.site_audit import SiteAuditRepository


async def run_site_audit(db: AsyncSession, request: AuditRequest) -> AuditResponse:
    score = random.randint(55, 98)
    issues = [
        IssueItem(severity="warning", message="Missing meta description on /about"),
        IssueItem(severity="error", message="Slow LCP (>2.5s) on mobile"),
        IssueItem(severity="info", message="Add structured data for breadcrumbs"),
    ]
    if score > 85:
        issues = [i for i in issues if i.severity != "error"]
    audit = SiteAudit(url=request.url, score=score, issues=str([i.model_dump() for i in issues]))
    await SiteAuditRepository(db).create(audit)
    return AuditResponse(url=request.url, score=score, issues=issues, created_at=datetime.utcnow())


async def research_keywords(db: AsyncSession, request: KeywordRequest) -> KeywordResponse:
    suggestions = [
        KeywordSuggestion(
            term=f"{request.seed} tools",
            search_volume=random.randint(1000, 50000),
            difficulty=random.randint(10, 60),
        ),
        KeywordSuggestion(
            term=f"best {request.seed}",
            search_volume=random.randint(2000, 80000),
            difficulty=random.randint(20, 70),
        ),
        KeywordSuggestion(
            term=f"{request.seed} tutorial",
            search_volume=random.randint(500, 25000),
            difficulty=random.randint(5, 40),
        ),
    ]
    kw = Keyword(
        term=request.seed,
        search_volume=suggestions[0].search_volume,
        difficulty=suggestions[0].difficulty,
        suggestions=str([s.model_dump() for s in suggestions]),
    )
    await KeywordRepository(db).create(kw)
    return KeywordResponse(seed=request.seed, suggestions=suggestions)


async def optimize_content(db: AsyncSession, request: ContentOptimizeRequest) -> ContentOptimizeResponse:
    optimized = (
        f"# {request.target_keyword.title()}\n\n"
        f"{request.content}\n\n"
        f"## Why {request.target_keyword.title()} Matters\n\n"
        f"In today's competitive landscape, **{request.target_keyword}** is essential. "
        f"This guide covers everything you need to know about {request.target_keyword}."
    )
    suggestions = [
        ContentSuggestion(type="structure", message="Add H2 subheadings every 300 words."),
        ContentSuggestion(type="keyword", message=f"Include '{request.target_keyword}' in the first 100 words."),
        ContentSuggestion(type="readability", message="Break paragraphs into 2-3 sentences."),
    ]
    record = ContentOptimization(
        target_keyword=request.target_keyword,
        original_content=request.content,
        optimized_content=optimized,
        suggestions=str([s.model_dump() for s in suggestions]),
    )
    await ContentOptimizationRepository(db).create(record)
    return ContentOptimizeResponse(
        target_keyword=request.target_keyword,
        optimized_content=optimized,
        suggestions=suggestions,
    )


async def track_rankings(db: AsyncSession, request: RankingsTrackRequest) -> RankingsTrackResponse:
    history = []
    base_pos = random.randint(3, 25)
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        pos = max(1, base_pos + random.randint(-2, 2))
        comp = max(1, pos + random.randint(-3, 3))
        history.append(RankDataPoint(date=date, position=pos, competitor_position=comp))
    ranking = Ranking(keyword=request.keyword, url=request.url, position=history[-1].position)
    await RankingRepository(db).create(ranking)
    return RankingsTrackResponse(keyword=request.keyword, url=request.url, history=history)

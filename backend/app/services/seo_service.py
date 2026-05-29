import hashlib
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_optimization import ContentOptimization
from app.models.keyword import Keyword
from app.models.ranking import Ranking
from app.models.site_audit import SiteAudit
from app.repositories.content_optimization import ContentOptimizationRepository
from app.repositories.keyword import KeywordRepository
from app.repositories.ranking import RankingRepository
from app.repositories.site_audit import SiteAuditRepository
from app.schemas.seo import (
    AuditRequest,
    AuditResponse,
    ContentOptimizeRequest,
    ContentOptimizeResponse,
    ContentSuggestion,
    IssueItem,
    KeywordRequest,
    KeywordResponse,
    KeywordSuggestion,
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


async def research_keywords(db: AsyncSession, request: KeywordRequest) -> KeywordResponse:
    seed = request.seed
    suggestions = [
        KeywordSuggestion(
            term=f"{seed} tools",
            search_volume=_stable_int(f"{seed} tools|vol", 1000, 50000),
            difficulty=_stable_int(f"{seed} tools|diff", 10, 60),
        ),
        KeywordSuggestion(
            term=f"best {seed}",
            search_volume=_stable_int(f"best {seed}|vol", 2000, 80000),
            difficulty=_stable_int(f"best {seed}|diff", 20, 70),
        ),
        KeywordSuggestion(
            term=f"{seed} tutorial",
            search_volume=_stable_int(f"{seed} tutorial|vol", 500, 25000),
            difficulty=_stable_int(f"{seed} tutorial|diff", 5, 40),
        ),
    ]
    kw = Keyword(
        term=seed,
        search_volume=suggestions[0].search_volume,
        difficulty=suggestions[0].difficulty,
        suggestions=json.dumps([s.model_dump() for s in suggestions]),
    )
    await KeywordRepository(db).create(kw)
    stored = [KeywordSuggestion(**s) for s in json.loads(kw.suggestions)]
    return KeywordResponse(seed=kw.term, suggestions=stored)


async def optimize_content(
    db: AsyncSession, request: ContentOptimizeRequest
) -> ContentOptimizeResponse:
    keyword = request.target_keyword
    optimized = (
        f"# {keyword.title()}\n\n"
        f"{request.content}\n\n"
        f"## Why {keyword.title()} Matters\n\n"
        f"In today's competitive landscape, **{keyword}** is essential. "
        f"This guide covers everything you need to know about {keyword}."
    )
    suggestions = [
        ContentSuggestion(type="structure", message="Add H2 subheadings every 300 words."),
        ContentSuggestion(
            type="keyword", message=f"Include '{keyword}' in the first 100 words."
        ),
        ContentSuggestion(type="readability", message="Break paragraphs into 2-3 sentences."),
    ]
    record = ContentOptimization(
        target_keyword=keyword,
        original_content=request.content,
        optimized_content=optimized,
        suggestions=json.dumps([s.model_dump() for s in suggestions]),
    )
    await ContentOptimizationRepository(db).create(record)
    stored = [ContentSuggestion(**s) for s in json.loads(record.suggestions)]
    return ContentOptimizeResponse(
        target_keyword=record.target_keyword,
        optimized_content=record.optimized_content,
        suggestions=stored,
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

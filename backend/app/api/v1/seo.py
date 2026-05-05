from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_db
from app.schemas.seo import (
    AuditRequest,
    AuditResponse,
    KeywordRequest,
    KeywordResponse,
    ContentOptimizeRequest,
    ContentOptimizeResponse,
    RankingsTrackRequest,
    RankingsTrackResponse,
)
from app.services.seo_service import (
    run_site_audit,
    research_keywords,
    optimize_content,
    track_rankings,
)

router = APIRouter(prefix="/seo", tags=["seo"])


@router.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest, db: AsyncSession = Depends(get_db)) -> AuditResponse:
    """Run a site audit and return mock crawl results."""
    return await run_site_audit(db, request)


@router.post("/keywords", response_model=KeywordResponse)
async def keywords(request: KeywordRequest, db: AsyncSession = Depends(get_db)) -> KeywordResponse:
    """Keyword research and suggestions."""
    return await research_keywords(db, request)


@router.post("/content/optimize", response_model=ContentOptimizeResponse)
async def content_optimize(
    request: ContentOptimizeRequest, db: AsyncSession = Depends(get_db)
) -> ContentOptimizeResponse:
    """Optimize content for a target keyword."""
    return await optimize_content(db, request)


@router.post("/rankings/track", response_model=RankingsTrackResponse)
async def rankings_track(
    request: RankingsTrackRequest, db: AsyncSession = Depends(get_db)
) -> RankingsTrackResponse:
    """Track keyword rankings over time."""
    return await track_rankings(db, request)

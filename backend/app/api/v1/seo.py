from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.services.content_optimizer import optimize_content
from app.services.keyword_research import research_keywords
from app.services.seo_data import ProviderUnavailable
from app.services.seo_service import (
    run_site_audit,
    track_rankings,
)

router = APIRouter(prefix="/seo", tags=["seo"])


@router.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest, db: AsyncSession = Depends(get_db)) -> AuditResponse:
    """Run a site audit and return mock crawl results."""
    return await run_site_audit(db, request)


@router.post("/keywords", response_model=KeywordResponse)
async def keywords(request: KeywordRequest, db: AsyncSession = Depends(get_db)) -> KeywordResponse:
    """Keyword research: real Google Suggest expansion + optional LLM enrichment."""
    try:
        return await research_keywords(db, request)
    except ProviderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


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

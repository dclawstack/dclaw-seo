from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.backlinks import BacklinkAnalyzeRequest, BacklinkAnalyzeResponse
from app.schemas.seo import (
    AuditRequest,
    AuditResponse,
    DashboardStats,
    KeywordRequest,
    KeywordResponse,
    ContentOptimizeRequest,
    ContentOptimizeResponse,
    RankingsTrackRequest,
    RankingsTrackResponse,
)
from app.schemas.competitor import CompetitorGapRequest, CompetitorGapResponse
from app.schemas.content_brief import ContentBriefRequest, ContentBriefResponse
from app.schemas.content_writer import ContentWriterRequest, ContentWriterResponse
from app.schemas.meta_tags import MetaTagsRequest, MetaTagsResponse
from app.schemas.performance import PerformanceRequest, PerformanceResponse
from app.schemas.video_seo import VideoSeoRequest, VideoSeoResponse
from app.services.backlinks import analyze_backlinks, list_backlinks
from app.services.competitor import CompetitorFetchError, competitor_gap
from app.services.content_brief import generate_brief
from app.services.content_optimizer import optimize_content
from app.services.content_writer import write_article
from app.services.copilot import PageFetchError
from app.services.keyword_research import research_keywords
from app.services.meta_tags import generate_meta_tags
from app.services.performance import PerfUnavailable, monitor_performance, performance_history
from app.services.rank_tracker import track_rankings
from app.services.seo_data import ProviderUnavailable
from app.services.site_auditor import run_site_audit
from app.services.stats import dashboard_stats
from app.services.video_seo import optimize_video

router = APIRouter(prefix="/seo", tags=["seo"])


@router.get("/stats", response_model=DashboardStats)
async def stats(db: AsyncSession = Depends(get_db)) -> DashboardStats:
    """Dashboard aggregates — real counts + recent activity from the DB."""
    return await dashboard_stats(db)


@router.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest, db: AsyncSession = Depends(get_db)) -> AuditResponse:
    """Run a real technical site audit (bounded internal crawl)."""
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


@router.post("/content/brief", response_model=ContentBriefResponse)
async def content_brief(
    request: ContentBriefRequest, db: AsyncSession = Depends(get_db)
) -> ContentBriefResponse:
    """Generate a content brief (outline, questions, length) from Suggest + LLM."""
    return await generate_brief(db, request)


@router.post("/content/write", response_model=ContentWriterResponse)
async def content_write(
    request: ContentWriterRequest, db: AsyncSession = Depends(get_db)
) -> ContentWriterResponse:
    """Generate a long-form article draft (LLM) with an originality + fact-check pass."""
    return await write_article(db, request)


@router.post("/meta", response_model=MetaTagsResponse)
async def meta_tags(
    request: MetaTagsRequest, db: AsyncSession = Depends(get_db)
) -> MetaTagsResponse:
    """Generate optimized title/meta/OG tags + JSON-LD schema for a URL or content."""
    try:
        return await generate_meta_tags(db, request)
    except PageFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/video", response_model=VideoSeoResponse)
async def video_seo(
    request: VideoSeoRequest, db: AsyncSession = Depends(get_db)
) -> VideoSeoResponse:
    """Optimize a video topic: 3 CTR title variants, description, tags, hashtags."""
    return await optimize_video(db, request)


@router.post("/rankings/track", response_model=RankingsTrackResponse)
async def rankings_track(
    request: RankingsTrackRequest, db: AsyncSession = Depends(get_db)
) -> RankingsTrackResponse:
    """Record a rank observation (SERP provider or manual) and return trend + alerts."""
    return await track_rankings(db, request)


@router.post("/backlinks/analyze", response_model=BacklinkAnalyzeResponse)
async def backlinks_analyze(
    request: BacklinkAnalyzeRequest, db: AsyncSession = Depends(get_db)
) -> BacklinkAnalyzeResponse:
    """Analyze backlinks for toxicity + detect new/lost (provider or supplied links)."""
    return await analyze_backlinks(db, request)


@router.get("/backlinks", response_model=BacklinkAnalyzeResponse)
async def backlinks_list(
    target_url: str, db: AsyncSession = Depends(get_db)
) -> BacklinkAnalyzeResponse:
    """List stored backlinks for a target."""
    return await list_backlinks(db, target_url)


@router.post("/performance", response_model=PerformanceResponse)
async def performance(
    request: PerformanceRequest, db: AsyncSession = Depends(get_db)
) -> PerformanceResponse:
    """Run a PageSpeed Insights (Core Web Vitals) check and record the trend."""
    try:
        return await monitor_performance(db, request)
    except PerfUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/performance", response_model=PerformanceResponse)
async def performance_trend(
    url: str, db: AsyncSession = Depends(get_db)
) -> PerformanceResponse:
    """Stored Core Web Vitals history for a URL."""
    return await performance_history(db, url)


@router.post("/competitor/gap", response_model=CompetitorGapResponse)
async def competitor_gap_analysis(
    request: CompetitorGapRequest, db: AsyncSession = Depends(get_db)
) -> CompetitorGapResponse:
    """Find content gaps vs a competitor (your Suggest keywords vs their page terms)."""
    try:
        return await competitor_gap(db, request)
    except CompetitorFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

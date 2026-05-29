from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.local_seo import (
    BusinessCreate,
    BusinessOut,
    CitationCreate,
    CitationOut,
    GbpSyncResult,
    NapScanResult,
    ReviewCreate,
    ReviewOut,
)
from app.repositories.local_seo import LocalBusinessRepository
from app.services import local_seo as svc

router = APIRouter(prefix="/local", tags=["local-seo"])


@router.post("/businesses", response_model=GbpSyncResult)
async def create_business(
    payload: BusinessCreate, db: AsyncSession = Depends(get_db)
) -> GbpSyncResult:
    """Register a business (GBP sync when GBP_API_KEY is set, else stored NAP)."""
    return await svc.sync_gbp(db, payload)


@router.get("/businesses", response_model=list[BusinessOut])
async def list_businesses(db: AsyncSession = Depends(get_db)) -> list[BusinessOut]:
    rows = await LocalBusinessRepository(db).list()
    return [BusinessOut.model_validate(r) for r in rows]


@router.post("/businesses/{business_id}/citations", response_model=CitationOut)
async def add_citation(
    business_id: int, payload: CitationCreate, db: AsyncSession = Depends(get_db)
) -> CitationOut:
    """Add a directory citation; NAP consistency is computed on insert."""
    try:
        return await svc.add_citation(db, business_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/businesses/{business_id}/nap-scan", response_model=NapScanResult)
async def nap_scan(business_id: int, db: AsyncSession = Depends(get_db)) -> NapScanResult:
    """Re-scan all citations for NAP consistency and return a score."""
    try:
        return await svc.nap_scan(db, business_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/businesses/{business_id}/reviews", response_model=ReviewOut)
async def add_review(
    business_id: int, payload: ReviewCreate, db: AsyncSession = Depends(get_db)
) -> ReviewOut:
    """Record a review and draft an AI-suggested response."""
    try:
        review = await svc.add_review(db, business_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ReviewOut.model_validate(review)


@router.get("/businesses/{business_id}/reviews", response_model=list[ReviewOut])
async def list_reviews(
    business_id: int, db: AsyncSession = Depends(get_db)
) -> list[ReviewOut]:
    rows = await svc.list_reviews(db, business_id)
    return [ReviewOut.model_validate(r) for r in rows]

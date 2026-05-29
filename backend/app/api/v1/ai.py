from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.ai import CopilotRequest, CopilotResponse
from app.services.copilot import PageFetchError, analyze_page
from app.services.llm_config import get_effective_config

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/copilot", response_model=CopilotResponse)
async def copilot(
    request: CopilotRequest, db: AsyncSession = Depends(get_db)
) -> CopilotResponse:
    """AI SEO Copilot: analyze a page and return prioritized next actions."""
    cfg = await get_effective_config(db)
    try:
        return await analyze_page(request.url, request.question, config=cfg)
    except PageFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

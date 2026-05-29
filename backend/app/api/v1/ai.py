from fastapi import APIRouter, HTTPException

from app.schemas.ai import CopilotRequest, CopilotResponse
from app.services.copilot import PageFetchError, analyze_page

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/copilot", response_model=CopilotResponse)
async def copilot(request: CopilotRequest) -> CopilotResponse:
    """AI SEO Copilot: analyze a page and return prioritized next actions."""
    try:
        return await analyze_page(request.url, request.question)
    except PageFetchError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

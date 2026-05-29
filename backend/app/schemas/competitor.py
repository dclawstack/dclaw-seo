from typing import List, Optional

from pydantic import BaseModel, Field


class CompetitorGapRequest(BaseModel):
    seed: str = Field(..., min_length=1, description="Your seed topic/keyword")
    competitor_url: str = Field(..., min_length=1, description="Competitor page URL")


class GapItem(BaseModel):
    term: str
    opportunity: int  # 0-100
    reason: Optional[str] = None


class CompetitorGapResponse(BaseModel):
    seed: str
    competitor_url: str
    your_keyword_count: int
    competitor_term_count: int
    gaps: List[GapItem]
    llm_enriched: bool = False
    note: Optional[str] = None

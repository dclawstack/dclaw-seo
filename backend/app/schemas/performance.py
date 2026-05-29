from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PerformanceRequest(BaseModel):
    url: str = Field(..., min_length=1)
    strategy: str = Field("mobile", description="mobile | desktop")


class PerfPoint(BaseModel):
    fetched_at: datetime
    score: Optional[int] = None
    lcp_ms: Optional[int] = None
    cls: Optional[float] = None


class PerformanceResponse(BaseModel):
    url: str
    strategy: str
    score: Optional[int] = None
    lcp_ms: Optional[int] = None
    cls: Optional[float] = None
    fcp_ms: Optional[int] = None
    tbt_ms: Optional[int] = None
    si_ms: Optional[int] = None
    recommendations: List[str] = Field(default_factory=list)
    history: List[PerfPoint] = Field(default_factory=list)
    note: Optional[str] = None

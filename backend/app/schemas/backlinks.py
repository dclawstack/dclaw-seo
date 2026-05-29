from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BacklinkInput(BaseModel):
    source_url: str = Field(..., min_length=1)
    anchor_text: Optional[str] = None


class BacklinkAnalyzeRequest(BaseModel):
    target_url: str = Field(..., min_length=1)
    links: List[BacklinkInput] = Field(default_factory=list)


class BacklinkItem(BaseModel):
    source_url: str
    anchor_text: Optional[str] = None
    toxic_score: Optional[int] = None
    toxic_reason: Optional[str] = None
    status: str
    first_seen: datetime
    last_seen: datetime


class BacklinkAnalyzeResponse(BaseModel):
    target_url: str
    total: int
    toxic_count: int
    new_count: int
    lost_count: int
    llm_enriched: bool = False
    note: Optional[str] = None
    backlinks: List[BacklinkItem]

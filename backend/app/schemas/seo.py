from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class AuditRequest(BaseModel):
    url: str = Field(..., min_length=1, description="URL to audit")


class IssueItem(BaseModel):
    severity: str
    message: str


class AuditResponse(BaseModel):
    url: str
    score: int
    issues: List[IssueItem]
    created_at: datetime


class KeywordRequest(BaseModel):
    seed: str = Field(..., min_length=1, description="Seed keyword")


class KeywordSuggestion(BaseModel):
    term: str
    intent: Optional[str] = None  # informational | transactional | navigational
    volume_band: Optional[str] = None  # low | medium | high (LLM estimate, not a count)
    difficulty_band: Optional[str] = None  # low | medium | high (LLM estimate)
    cluster: Optional[str] = None


class KeywordResponse(BaseModel):
    seed: str
    suggestions: List[KeywordSuggestion]
    llm_enriched: bool = False
    note: Optional[str] = None


class ContentOptimizeRequest(BaseModel):
    target_keyword: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class ContentSuggestion(BaseModel):
    type: str
    message: str


class ContentOptimizeResponse(BaseModel):
    target_keyword: str
    optimized_content: str
    suggestions: List[ContentSuggestion]


class RankingsTrackRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)


class RankDataPoint(BaseModel):
    date: str
    position: int
    competitor_position: int


class RankingsTrackResponse(BaseModel):
    keyword: str
    url: str
    history: List[RankDataPoint]

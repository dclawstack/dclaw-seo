from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class AuditRequest(BaseModel):
    url: str = Field(..., min_length=1, description="URL to audit")
    max_pages: int = Field(10, ge=1, le=25, description="Max internal pages to crawl")


class IssueItem(BaseModel):
    severity: str  # error | warning | info
    message: str
    type: Optional[str] = None  # issue category, e.g. missing_title
    url: Optional[str] = None  # page the issue was found on


class AuditResponse(BaseModel):
    url: str
    score: int
    pages_crawled: int = 0
    issues: List[IssueItem]
    summary: Optional[str] = None
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
    score: int  # 0-100
    readability: float  # Flesch reading ease
    keyword_density: float  # percent
    word_count: int
    optimized_content: Optional[str] = None  # LLM rewrite ("after"); None without LLM
    suggestions: List[ContentSuggestion]
    llm_enriched: bool = False
    note: Optional[str] = None


class RankingsTrackRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    position: Optional[int] = Field(
        None, ge=1, description="Manually observed SERP position (real data, no SERP provider needed)"
    )


class RankDataPoint(BaseModel):
    date: str
    position: int
    competitor_position: Optional[int] = None


class RankingsTrackResponse(BaseModel):
    keyword: str
    url: str
    history: List[RankDataPoint]
    alerts: List[str] = []
    serp_source: str = "none"
    note: Optional[str] = None


class ActivityItem(BaseModel):
    type: str  # audit | keyword | content | ranking
    label: str
    at: datetime


class DashboardStats(BaseModel):
    audits: int
    keywords: int
    optimizations: int
    rank_observations: int
    latest_audit_score: Optional[int] = None
    recent: List[ActivityItem]

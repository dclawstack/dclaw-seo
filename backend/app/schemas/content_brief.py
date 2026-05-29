from typing import List, Optional

from pydantic import BaseModel, Field


class ContentBriefRequest(BaseModel):
    keyword: str = Field(..., min_length=1)


class BriefSection(BaseModel):
    h2: str
    h3: List[str] = Field(default_factory=list)


class ContentBriefResponse(BaseModel):
    keyword: str
    title_suggestions: List[str]
    outline: List[BriefSection]
    questions: List[str]
    recommended_words: int
    secondary_keywords: List[str]
    llm_enriched: bool = False
    note: Optional[str] = None

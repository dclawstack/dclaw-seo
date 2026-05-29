from typing import List, Optional

from pydantic import BaseModel, Field


class ContentWriterRequest(BaseModel):
    keyword: str = Field(..., min_length=1, description="Primary target keyword / topic")
    tone: str = Field("professional", description="professional | casual | persuasive | technical")
    target_words: int = Field(1000, ge=300, le=3000)
    outline: Optional[List[str]] = Field(
        default=None, description="Optional H2 headings; auto-derived from Suggest when omitted"
    )


class ArticleSection(BaseModel):
    heading: str
    body: str


class ContentWriterResponse(BaseModel):
    keyword: str
    title: str
    sections: List[ArticleSection]
    word_count: int
    # Originality: share of repeated 5-grams within the draft (lower = more original).
    # This is an internal redundancy check, NOT a web plagiarism scan — see `note`.
    originality_score: float = Field(..., description="0-100; 100 = fully unique 5-grams")
    fact_check_notes: List[str] = Field(default_factory=list)
    llm_generated: bool = False
    note: Optional[str] = None

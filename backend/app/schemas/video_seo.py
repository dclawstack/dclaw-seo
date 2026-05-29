from typing import List, Optional

from pydantic import BaseModel, Field


class VideoSeoRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Video topic / working title")
    keywords: Optional[List[str]] = Field(default=None, description="Optional seed keywords")
    transcript: Optional[str] = Field(default=None, description="Optional transcript for context")


class VideoTitleVariant(BaseModel):
    title: str
    angle: str  # e.g. "how-to", "listicle", "curiosity"


class VideoSeoResponse(BaseModel):
    topic: str
    title_variants: List[VideoTitleVariant]
    description: str
    tags: List[str]
    hashtags: List[str]
    llm_enriched: bool = False
    note: Optional[str] = None

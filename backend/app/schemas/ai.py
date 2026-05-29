from typing import List, Optional

from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    url: str = Field(..., min_length=1, description="Page URL to analyze")
    question: Optional[str] = Field(None, description="Optional question for the copilot")


class PageSignals(BaseModel):
    title: Optional[str] = None
    title_length: int = 0
    meta_description: Optional[str] = None
    meta_length: int = 0
    h1_count: int = 0
    word_count: int = 0
    readability: float = 0.0


class CopilotAction(BaseModel):
    priority: int  # 1 = highest
    category: str  # title | meta | content | structure | links
    title: str
    detail: str


class CopilotResponse(BaseModel):
    url: str
    summary: str
    signals: PageSignals
    actions: List[CopilotAction]
    llm_enriched: bool = False
    note: Optional[str] = None

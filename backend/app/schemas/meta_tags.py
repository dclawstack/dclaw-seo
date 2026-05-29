from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class MetaTagsRequest(BaseModel):
    url: Optional[str] = Field(default=None, description="Page URL to fetch and optimize")
    content: Optional[str] = Field(default=None, description="Raw content/HTML when no URL")
    keyword: Optional[str] = Field(default=None, description="Primary keyword to target")

    @model_validator(mode="after")
    def _need_source(self) -> "MetaTagsRequest":
        if not self.url and not self.content:
            raise ValueError("Provide either `url` or `content`.")
        return self


class MetaTagsResponse(BaseModel):
    title_tag: str
    title_length: int
    meta_description: str
    meta_length: int
    og_tags: Dict[str, str]
    twitter_tags: Dict[str, str]
    json_ld: Dict[str, Any]
    title_variants: List[str] = Field(default_factory=list)
    llm_enriched: bool = False
    note: Optional[str] = None

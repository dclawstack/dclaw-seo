from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BusinessCreate(BaseModel):
    name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    website: Optional[str] = None
    gbp_place_id: Optional[str] = None


class BusinessOut(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    website: Optional[str] = None
    gbp_place_id: Optional[str] = None

    model_config = {"from_attributes": True}


class CitationCreate(BaseModel):
    source: str = Field(..., min_length=1)
    url: Optional[str] = None
    listed_name: str = Field(..., min_length=1)
    listed_address: str = Field(..., min_length=1)
    listed_phone: str = Field(..., min_length=1)


class CitationOut(BaseModel):
    id: int
    source: str
    url: Optional[str] = None
    listed_name: str
    listed_address: str
    listed_phone: str
    nap_consistent: bool
    mismatch_fields: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class NapScanResult(BaseModel):
    business_id: int
    total_citations: int
    consistent: int
    inconsistent: int
    consistency_score: float  # 0-100
    citations: List[CitationOut]


class ReviewCreate(BaseModel):
    source: str = Field(..., min_length=1)
    author: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    source: str
    author: Optional[str] = None
    rating: int
    text: Optional[str] = None
    suggested_response: Optional[str] = None
    responded: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class GbpSyncResult(BaseModel):
    business: BusinessOut
    synced_from_gbp: bool
    note: Optional[str] = None

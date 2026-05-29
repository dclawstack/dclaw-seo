from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)
    domain: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    org_id: int
    name: str
    domain: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class OrgCapUpdate(BaseModel):
    monthly_cost_cap_usd: Optional[float] = Field(
        default=None, ge=0, description="Null clears the cap"
    )


class LedgerEntry(BaseModel):
    id: int
    feature: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
    created_at: datetime

    model_config = {"from_attributes": True}


class UsageSummary(BaseModel):
    org_id: int
    month_to_date_cost_usd: float
    monthly_cost_cap_usd: Optional[float] = None
    over_cap: bool
    recent: List[LedgerEntry]

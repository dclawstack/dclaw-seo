from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportBranding(BaseModel):
    title: str = "SEO Performance Report"
    brand_company: Optional[str] = None
    brand_color: Optional[str] = Field(default=None, description="Hex, e.g. #6E56CF")


class ReportRequest(ReportBranding):
    site_url: Optional[str] = None


class ReportMetric(BaseModel):
    label: str
    value: str


class ReportPreview(BaseModel):
    title: str
    brand_company: Optional[str] = None
    generated_at: datetime
    metrics: List[ReportMetric]
    executive_summary: str
    summary_ai: bool = False
    note: Optional[str] = None


class ScheduleCreate(BaseModel):
    site_url: str = Field(..., min_length=1)
    frequency: str = Field("weekly", pattern="^(daily|weekly|monthly)$")
    recipient: str = Field(..., min_length=3)
    brand_company: Optional[str] = None
    brand_color: Optional[str] = None


class ScheduleOut(BaseModel):
    id: int
    site_url: str
    frequency: str
    recipient: str
    brand_company: Optional[str] = None
    brand_color: Optional[str] = None
    last_run_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScheduleRunResult(BaseModel):
    schedule_id: int
    recipient: str
    delivered: bool
    detail: str

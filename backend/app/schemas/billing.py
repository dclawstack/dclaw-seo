from typing import List, Optional

from pydantic import BaseModel, Field


class PlanInfo(BaseModel):
    key: str
    name: str
    monthly_price_usd: float
    included_seats: int
    price_per_extra_seat_usd: float
    included_usage_usd: float  # LLM cost included before overage


class BillingAccountOut(BaseModel):
    org_id: int
    plan: str
    seats: int
    status: str
    stripe_customer_id: Optional[str] = None
    stripe_enabled: bool

    model_config = {"from_attributes": True}


class SubscribeRequest(BaseModel):
    plan: str = Field(..., pattern="^(free|starter|pro)$")
    seats: int = Field(1, ge=1, le=1000)


class InvoiceLine(BaseModel):
    description: str
    amount_usd: float


class InvoicePreview(BaseModel):
    org_id: int
    plan: str
    seats: int
    period: str  # YYYY-MM
    lines: List[InvoiceLine]
    usage_cost_usd: float
    total_usd: float
    stripe_enabled: bool
    note: Optional[str] = None

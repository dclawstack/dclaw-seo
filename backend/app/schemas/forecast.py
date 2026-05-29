from typing import List, Optional

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    horizon: int = Field(4, ge=1, le=12, description="How many future checks to project")


class ForecastPoint(BaseModel):
    step: int  # 1..horizon
    position: float


class ForecastResponse(BaseModel):
    keyword: str
    url: str
    data_points: int
    current_position: Optional[float] = None
    slope_per_check: Optional[float] = None  # negative = improving (rank getting smaller)
    trend: str  # improving | declining | stable | insufficient_data
    confidence: str  # high | medium | low | none
    competitor_pressure: Optional[str] = None  # gaining | easing | stable
    forecast: List[ForecastPoint] = Field(default_factory=list)
    note: Optional[str] = None

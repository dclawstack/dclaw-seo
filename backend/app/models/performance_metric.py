from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PerformanceMetric(Base):
    """A Core Web Vitals / Lighthouse observation for a URL (for trends)."""

    __tablename__ = "performance_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    strategy: Mapped[str] = mapped_column(String(16), default="mobile")
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0-100
    lcp_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cls: Mapped[float | None] = mapped_column(Float, nullable=True)
    fcp_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tbt_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    si_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ReportSchedule(Base):
    """A recurring white-label report delivery configuration."""

    __tablename__ = "report_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_url: Mapped[str] = mapped_column(String(512), nullable=False)
    frequency: Mapped[str] = mapped_column(String(16), default="weekly")  # daily|weekly|monthly
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    brand_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_color: Mapped[str | None] = mapped_column(String(16), nullable=True)  # hex
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

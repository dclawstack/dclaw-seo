from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class SiteAudit(Base):
    __tablename__ = "site_audits"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    issues: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

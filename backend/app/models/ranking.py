from datetime import datetime
from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    competitor_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tracked_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

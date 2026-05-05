from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class ContentOptimization(Base):
    __tablename__ = "content_optimizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    target_keyword: Mapped[str] = mapped_column(String(512), nullable=False)
    original_content: Mapped[str] = mapped_column(Text, nullable=False)
    optimized_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

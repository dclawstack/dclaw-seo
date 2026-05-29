from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LLMSettings(Base):
    """Single-row (id=1) runtime LLM configuration, editable from the app.

    Null/blank fields fall back to the environment defaults.
    """

    __tablename__ = "llm_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ollama_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    ollama_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    openrouter_api_key: Mapped[str | None] = mapped_column(String(256), nullable=True)
    openrouter_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

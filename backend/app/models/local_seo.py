from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LocalBusiness(Base):
    """A business location with its canonical NAP (Name / Address / Phone)."""

    __tablename__ = "local_businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(512), nullable=False)
    phone: Mapped[str] = mapped_column(String(64), nullable=False)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gbp_place_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Citation(Base):
    """A directory listing (Yelp, YellowPages, …) with its listed NAP."""

    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("local_businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    listed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    listed_address: Mapped[str] = mapped_column(String(512), nullable=False)
    listed_phone: Mapped[str] = mapped_column(String(64), nullable=False)
    nap_consistent: Mapped[bool] = mapped_column(Boolean, default=True)
    mismatch_fields: Mapped[str | None] = mapped_column(Text, nullable=True)  # csv: name,phone
    last_checked: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Review(Base):
    """A customer review plus an optional AI-suggested response."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("local_businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    responded: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

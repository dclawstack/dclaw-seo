from collections.abc import Sequence

from sqlalchemy import select

from app.models.local_seo import Citation, LocalBusiness, Review
from app.repositories.base import BaseRepository


class LocalBusinessRepository(BaseRepository[LocalBusiness]):
    model = LocalBusiness


class CitationRepository(BaseRepository[Citation]):
    model = Citation

    async def for_business(self, business_id: int) -> Sequence[Citation]:
        result = await self.db.execute(
            select(Citation).where(Citation.business_id == business_id).order_by(Citation.source)
        )
        return result.scalars().all()


class ReviewRepository(BaseRepository[Review]):
    model = Review

    async def for_business(self, business_id: int) -> Sequence[Review]:
        result = await self.db.execute(
            select(Review)
            .where(Review.business_id == business_id)
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()

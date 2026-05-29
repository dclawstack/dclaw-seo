from collections.abc import Sequence

from sqlalchemy import select

from app.models.content_optimization import ContentOptimization
from app.repositories.base import BaseRepository


class ContentOptimizationRepository(BaseRepository[ContentOptimization]):
    model = ContentOptimization

    async def recent(self, limit: int = 5) -> Sequence[ContentOptimization]:
        result = await self.db.execute(
            select(ContentOptimization)
            .order_by(ContentOptimization.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

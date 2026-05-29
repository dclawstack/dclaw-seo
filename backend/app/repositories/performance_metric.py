from collections.abc import Sequence

from sqlalchemy import select

from app.models.performance_metric import PerformanceMetric
from app.repositories.base import BaseRepository


class PerformanceMetricRepository(BaseRepository[PerformanceMetric]):
    model = PerformanceMetric

    async def history(self, url: str, limit: int = 30) -> Sequence[PerformanceMetric]:
        result = await self.db.execute(
            select(PerformanceMetric)
            .where(PerformanceMetric.url == url)
            .order_by(PerformanceMetric.fetched_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

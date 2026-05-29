from collections.abc import Sequence

from sqlalchemy import select

from app.models.ranking import Ranking
from app.repositories.base import BaseRepository


class RankingRepository(BaseRepository[Ranking]):
    model = Ranking

    async def history(self, keyword: str, url: str, limit: int = 30) -> Sequence[Ranking]:
        result = await self.db.execute(
            select(Ranking)
            .where(Ranking.keyword == keyword, Ranking.url == url)
            .order_by(Ranking.tracked_at.asc())
            .limit(limit)
        )
        return result.scalars().all()

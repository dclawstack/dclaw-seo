from collections.abc import Sequence

from sqlalchemy import select

from app.models.keyword import Keyword
from app.repositories.base import BaseRepository


class KeywordRepository(BaseRepository[Keyword]):
    model = Keyword

    async def recent(self, limit: int = 5) -> Sequence[Keyword]:
        result = await self.db.execute(
            select(Keyword).order_by(Keyword.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

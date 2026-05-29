from collections.abc import Sequence

from sqlalchemy import select

from app.models.backlink import Backlink
from app.repositories.base import BaseRepository


class BacklinkRepository(BaseRepository[Backlink]):
    model = Backlink

    async def for_target(self, target_url: str) -> Sequence[Backlink]:
        result = await self.db.execute(
            select(Backlink)
            .where(Backlink.target_url == target_url)
            .order_by(Backlink.toxic_score.desc().nullslast())
        )
        return result.scalars().all()

    async def find(self, target_url: str, source_url: str) -> Backlink | None:
        result = await self.db.execute(
            select(Backlink).where(
                Backlink.target_url == target_url, Backlink.source_url == source_url
            )
        )
        return result.scalar_one_or_none()

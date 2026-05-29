from collections.abc import Sequence

from sqlalchemy import select

from app.models.site_audit import SiteAudit
from app.repositories.base import BaseRepository


class SiteAuditRepository(BaseRepository[SiteAudit]):
    model = SiteAudit

    async def recent(self, limit: int = 5) -> Sequence[SiteAudit]:
        result = await self.db.execute(
            select(SiteAudit).order_by(SiteAudit.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

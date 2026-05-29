from sqlalchemy import select

from app.models.billing import BillingAccount
from app.repositories.base import BaseRepository


class BillingAccountRepository(BaseRepository[BillingAccount]):
    model = BillingAccount

    async def for_org(self, org_id: int) -> BillingAccount | None:
        result = await self.db.execute(
            select(BillingAccount).where(BillingAccount.org_id == org_id)
        )
        return result.scalar_one_or_none()

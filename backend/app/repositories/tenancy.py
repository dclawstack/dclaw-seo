from collections.abc import Sequence

from sqlalchemy import select

from app.models.tenancy import LlmCostLedger, Organization, Project, User
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    model = Organization


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


class ProjectRepository(BaseRepository[Project]):
    model = Project

    async def for_org(self, org_id: int) -> Sequence[Project]:
        result = await self.db.execute(
            select(Project).where(Project.org_id == org_id).order_by(Project.created_at.desc())
        )
        return result.scalars().all()


class CostLedgerRepository(BaseRepository[LlmCostLedger]):
    model = LlmCostLedger

    async def recent_for_org(self, org_id: int, limit: int = 50) -> Sequence[LlmCostLedger]:
        result = await self.db.execute(
            select(LlmCostLedger)
            .where(LlmCostLedger.org_id == org_id)
            .order_by(LlmCostLedger.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

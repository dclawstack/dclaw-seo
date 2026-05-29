from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_deps import get_current_user
from app.core.database import get_db
from app.models.tenancy import Organization, Project, User
from app.repositories.tenancy import (
    CostLedgerRepository,
    OrganizationRepository,
    ProjectRepository,
)
from app.schemas.auth import OrgOut
from app.schemas.tenancy import (
    LedgerEntry,
    OrgCapUpdate,
    ProjectCreate,
    ProjectOut,
    UsageSummary,
)
from app.services import metering

router = APIRouter(prefix="/org", tags=["organization"])


@router.get("", response_model=OrgOut)
async def get_org(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> OrgOut:
    org = await db.get(Organization, user.org_id)
    return OrgOut.model_validate(org)


@router.put("/cost-cap", response_model=OrgOut)
async def set_cost_cap(
    payload: OrgCapUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgOut:
    org = await db.get(Organization, user.org_id)
    org.monthly_cost_cap_usd = payload.monthly_cost_cap_usd
    await db.commit()
    await db.refresh(org)
    return OrgOut.model_validate(org)


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ProjectOut]:
    rows = await ProjectRepository(db).for_org(user.org_id)
    return [ProjectOut.model_validate(r) for r in rows]


@router.post("/projects", response_model=ProjectOut)
async def create_project(
    payload: ProjectCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectOut:
    project = await ProjectRepository(db).create(
        Project(org_id=user.org_id, name=payload.name, domain=payload.domain)
    )
    return ProjectOut.model_validate(project)


@router.get("/usage", response_model=UsageSummary)
async def usage(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> UsageSummary:
    org = await OrganizationRepository(db).get(user.org_id)
    spent = await metering.month_to_date_cost(db, user.org_id)
    recent = await CostLedgerRepository(db).recent_for_org(user.org_id)
    cap = org.monthly_cost_cap_usd if org else None
    return UsageSummary(
        org_id=user.org_id,
        month_to_date_cost_usd=round(spent, 6),
        monthly_cost_cap_usd=cap,
        over_cap=cap is not None and spent >= cap,
        recent=[LedgerEntry.model_validate(r) for r in recent],
    )

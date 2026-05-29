from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_deps import get_current_user
from app.core.database import get_db
from app.models.tenancy import User
from app.schemas.billing import (
    BillingAccountOut,
    InvoicePreview,
    PlanInfo,
    SubscribeRequest,
)
from app.services import billing as svc

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanInfo])
async def plans() -> list[PlanInfo]:
    return svc.list_plans()


@router.get("/account", response_model=BillingAccountOut)
async def account(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> BillingAccountOut:
    return await svc.get_account(db, user.org_id)


@router.put("/subscribe", response_model=BillingAccountOut)
async def subscribe(
    payload: SubscribeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BillingAccountOut:
    return await svc.subscribe(db, user.org_id, payload)


@router.get("/invoice/preview", response_model=InvoicePreview)
async def invoice_preview(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> InvoicePreview:
    return await svc.invoice_preview(db, user.org_id)

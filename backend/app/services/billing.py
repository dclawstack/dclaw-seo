"""Billing: plans, per-seat + metered invoicing, optional Stripe.

The invoice is computed locally and truthfully from real data: the plan base
price, per-seat overage, and **usage overage taken from the LLM cost ledger**
(``services/metering``). Stripe is optional — when ``STRIPE_API_KEY`` is set we
create/lookup a Stripe customer (REST via httpx, no SDK dependency); when it is
not, billing runs in local mode and says so. We never fabricate a charge.
"""

from __future__ import annotations

from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.billing import BillingAccount
from app.repositories.billing import BillingAccountRepository
from app.schemas.billing import (
    BillingAccountOut,
    InvoiceLine,
    InvoicePreview,
    PlanInfo,
    SubscribeRequest,
)
from app.services import metering

logger = get_logger(__name__)

PLANS: dict[str, PlanInfo] = {
    "free": PlanInfo(
        key="free", name="Free", monthly_price_usd=0.0, included_seats=1,
        price_per_extra_seat_usd=0.0, included_usage_usd=0.0,
    ),
    "starter": PlanInfo(
        key="starter", name="Starter", monthly_price_usd=29.0, included_seats=3,
        price_per_extra_seat_usd=9.0, included_usage_usd=5.0,
    ),
    "pro": PlanInfo(
        key="pro", name="Pro", monthly_price_usd=99.0, included_seats=10,
        price_per_extra_seat_usd=7.0, included_usage_usd=25.0,
    ),
}


def stripe_enabled() -> bool:
    return bool(settings.stripe_api_key)


def _out(account: BillingAccount) -> BillingAccountOut:
    return BillingAccountOut(
        org_id=account.org_id,
        plan=account.plan,
        seats=account.seats,
        status=account.status,
        stripe_customer_id=account.stripe_customer_id,
        stripe_enabled=stripe_enabled(),
    )


async def get_or_create_account(db: AsyncSession, org_id: int) -> BillingAccount:
    repo = BillingAccountRepository(db)
    account = await repo.for_org(org_id)
    if account is None:
        account = await repo.create(BillingAccount(org_id=org_id, plan="free", seats=1))
    return account


async def _stripe_create_customer(org_id: int, plan: str) -> str | None:
    """Create a Stripe customer via REST. Returns customer id or None on failure."""
    if not stripe_enabled():
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{settings.stripe_base_url}/customers",
                auth=(settings.stripe_api_key, ""),
                data={"description": f"DClaw SEO org {org_id}", "metadata[plan]": plan},
            )
            resp.raise_for_status()
            return resp.json().get("id")
    except httpx.HTTPError as exc:
        logger.warning("stripe_customer_failed", error=str(exc))
        return None


async def subscribe(db: AsyncSession, org_id: int, payload: SubscribeRequest) -> BillingAccountOut:
    account = await get_or_create_account(db, org_id)
    account.plan = payload.plan
    account.seats = payload.seats
    if stripe_enabled() and account.stripe_customer_id is None and payload.plan != "free":
        account.stripe_customer_id = await _stripe_create_customer(org_id, payload.plan)
    await db.commit()
    await db.refresh(account)
    return _out(account)


async def get_account(db: AsyncSession, org_id: int) -> BillingAccountOut:
    return _out(await get_or_create_account(db, org_id))


async def invoice_preview(db: AsyncSession, org_id: int) -> InvoicePreview:
    account = await get_or_create_account(db, org_id)
    plan = PLANS.get(account.plan, PLANS["free"])
    now = datetime.now(timezone.utc)
    usage_cost = await metering.month_to_date_cost(db, org_id)

    lines: list[InvoiceLine] = []
    if plan.monthly_price_usd:
        lines.append(InvoiceLine(description=f"{plan.name} plan (base)", amount_usd=plan.monthly_price_usd))
    extra_seats = max(0, account.seats - plan.included_seats)
    if extra_seats:
        lines.append(
            InvoiceLine(
                description=f"{extra_seats} extra seat(s) x ${plan.price_per_extra_seat_usd:.2f}",
                amount_usd=round(extra_seats * plan.price_per_extra_seat_usd, 2),
            )
        )
    usage_overage = round(max(0.0, usage_cost - plan.included_usage_usd), 4)
    if usage_overage:
        lines.append(InvoiceLine(description="LLM usage overage", amount_usd=usage_overage))

    total = round(sum(line.amount_usd for line in lines), 4)
    return InvoicePreview(
        org_id=org_id,
        plan=account.plan,
        seats=account.seats,
        period=now.strftime("%Y-%m"),
        lines=lines,
        usage_cost_usd=round(usage_cost, 6),
        total_usd=total,
        stripe_enabled=stripe_enabled(),
        note=(
            None
            if stripe_enabled()
            else "Local invoice (Stripe not configured). Set STRIPE_API_KEY to sync customers "
            "and push invoices to Stripe."
        ),
    )


def list_plans() -> list[PlanInfo]:
    return list(PLANS.values())

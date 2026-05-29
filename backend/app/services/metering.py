"""Per-organization LLM cost metering: ledger writes, monthly spend, cost cap.

Reads/writes through the caller's request session (carried on the
:class:`~app.core.context.Meter`) so it works identically under tests and in
production. Token usage is recorded for every metered call; cost is derived from
a configurable per-1k-token rate (local Ollama is effectively $0 but is still
recorded, so usage is always truthful).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.tenancy import LlmCostLedger, Organization


class QuotaExceeded(RuntimeError):
    """Raised when an organization is at/over its monthly LLM cost cap."""


def _month_start(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def token_cost(prompt_tokens: int, completion_tokens: int) -> float:
    total = prompt_tokens + completion_tokens
    return round(total / 1000 * settings.llm_cost_per_1k_tokens_usd, 6)


async def month_to_date_cost(db: AsyncSession, org_id: int, now: datetime | None = None) -> float:
    now = now or datetime.now(timezone.utc)
    start = _month_start(now)
    result = await db.execute(
        select(func.coalesce(func.sum(LlmCostLedger.cost_usd), 0.0)).where(
            LlmCostLedger.org_id == org_id, LlmCostLedger.created_at >= start
        )
    )
    return float(result.scalar_one())


async def enforce_cap(db: AsyncSession, org_id: int) -> None:
    org = await db.get(Organization, org_id)
    if org is None or org.monthly_cost_cap_usd is None:
        return
    spent = await month_to_date_cost(db, org_id)
    if spent >= org.monthly_cost_cap_usd:
        raise QuotaExceeded(
            f"Organization is over its monthly LLM cost cap "
            f"(${spent:.4f} / ${org.monthly_cost_cap_usd:.2f})."
        )


async def record(
    db: AsyncSession,
    org_id: int,
    feature: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> LlmCostLedger:
    row = LlmCostLedger(
        org_id=org_id,
        feature=feature,
        model=model or "unknown",
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_usd=token_cost(prompt_tokens, completion_tokens),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row

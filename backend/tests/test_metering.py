import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenancy import Organization
from app.services import metering
from app.services.metering import QuotaExceeded
from tests.conftest import TEST_ORG_ID, test_engine


async def _session() -> AsyncSession:
    return AsyncSession(test_engine, expire_on_commit=False)


def test_token_cost_zero_by_default():
    # default rate is 0.0 (local Ollama) -> always 0 cost, still recorded
    assert metering.token_cost(1000, 2000) == 0.0


@pytest.mark.asyncio
async def test_record_and_month_to_date():
    async with await _session() as db:
        await metering.record(db, TEST_ORG_ID, "test", "llama3.2:3b", 100, 50)
        await metering.record(db, TEST_ORG_ID, "test", "llama3.2:3b", 10, 5)
        total = await metering.month_to_date_cost(db, TEST_ORG_ID)
        assert total == 0.0  # rate 0


@pytest.mark.asyncio
async def test_cap_enforced_when_over():
    async with await _session() as db:
        org = await db.get(Organization, TEST_ORG_ID)
        org.monthly_cost_cap_usd = 0.0  # any spend >= 0 trips it
        # seed a ledger row with nonzero cost by monkeypatching the rate
        from app.core.config import settings

        saved = settings.llm_cost_per_1k_tokens_usd
        settings.llm_cost_per_1k_tokens_usd = 1.0
        try:
            await metering.record(db, TEST_ORG_ID, "test", "m", 1000, 0)  # $1
            with pytest.raises(QuotaExceeded):
                await metering.enforce_cap(db, TEST_ORG_ID)
        finally:
            settings.llm_cost_per_1k_tokens_usd = saved


@pytest.mark.asyncio
async def test_no_cap_never_raises():
    async with await _session() as db:
        org = await db.get(Organization, TEST_ORG_ID)
        org.monthly_cost_cap_usd = None
        await db.commit()
        await metering.enforce_cap(db, TEST_ORG_ID)  # should not raise


@pytest.mark.asyncio
async def test_usage_endpoint(client):
    r = await client.get("/api/v1/org/usage")
    assert r.status_code == 200
    body = r.json()
    assert body["org_id"] == TEST_ORG_ID
    assert "month_to_date_cost_usd" in body
    assert body["over_cap"] is False

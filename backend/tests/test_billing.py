import pytest

from app.services import billing
from app.services.billing import PLANS


def test_plans_present():
    assert {"free", "starter", "pro"} <= set(PLANS)
    assert PLANS["pro"].monthly_price_usd == 99.0


def test_stripe_disabled_by_default():
    assert billing.stripe_enabled() is False


@pytest.mark.asyncio
async def test_default_account_is_free(client):
    r = await client.get("/api/v1/billing/account")
    assert r.status_code == 200
    body = r.json()
    assert body["plan"] == "free"
    assert body["stripe_enabled"] is False


@pytest.mark.asyncio
async def test_plans_endpoint(client):
    r = await client.get("/api/v1/billing/plans")
    assert r.status_code == 200
    assert len(r.json()) == 3


@pytest.mark.asyncio
async def test_subscribe_and_invoice(client):
    r = await client.put("/api/v1/billing/subscribe", json={"plan": "starter", "seats": 5})
    assert r.status_code == 200
    assert r.json()["plan"] == "starter"
    assert r.json()["seats"] == 5

    r = await client.get("/api/v1/billing/invoice/preview")
    assert r.status_code == 200
    inv = r.json()
    assert inv["plan"] == "starter"
    # base 29 + 2 extra seats * 9 = 47 (local Ollama usage is $0 -> no overage)
    assert inv["total_usd"] == pytest.approx(47.0)
    assert any("base" in line["description"] for line in inv["lines"])
    assert any("extra seat" in line["description"] for line in inv["lines"])


@pytest.mark.asyncio
async def test_free_plan_zero_invoice(client):
    await client.put("/api/v1/billing/subscribe", json={"plan": "free", "seats": 1})
    r = await client.get("/api/v1/billing/invoice/preview")
    assert r.json()["total_usd"] == 0.0

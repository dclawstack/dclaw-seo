import pytest


@pytest.mark.asyncio
async def test_audit_returns_persisted_result(client):
    resp = await client.post("/api/v1/seo/audit", json={"url": "https://example.com"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["url"] == "https://example.com"
    assert isinstance(body["score"], int)
    assert 0 <= body["score"] <= 100
    assert len(body["issues"]) >= 1
    assert {"severity", "message"} <= body["issues"][0].keys()
    assert body["created_at"]


@pytest.mark.asyncio
async def test_audit_is_deterministic(client):
    first = await client.post("/api/v1/seo/audit", json={"url": "https://acme.dev"})
    second = await client.post("/api/v1/seo/audit", json={"url": "https://acme.dev"})
    assert first.json()["score"] == second.json()["score"]


@pytest.mark.asyncio
async def test_audit_rejects_empty_url(client):
    resp = await client.post("/api/v1/seo/audit", json={"url": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_rankings_track_history_grows(client):
    payload = {"keyword": "latte art", "url": "https://shop.example"}
    first = await client.post("/api/v1/seo/rankings/track", json=payload)
    second = await client.post("/api/v1/seo/rankings/track", json=payload)
    assert first.status_code == 200
    assert len(first.json()["history"]) == 1
    # second call reads real persisted rows back -> history grows
    assert len(second.json()["history"]) == 2
    point = second.json()["history"][0]
    assert {"date", "position", "competitor_position"} <= point.keys()

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
async def test_rankings_track_records_manual_positions(client):
    base = {"keyword": "latte art", "url": "https://shop.example"}
    first = await client.post("/api/v1/seo/rankings/track", json={**base, "position": 4})
    second = await client.post("/api/v1/seo/rankings/track", json={**base, "position": 6})
    assert first.status_code == 200
    assert len(first.json()["history"]) == 1
    body = second.json()
    assert len(body["history"]) == 2  # real persisted observations grow
    assert body["serp_source"] == "manual"
    assert {"date", "position", "competitor_position"} <= body["history"][0].keys()


@pytest.mark.asyncio
async def test_rankings_track_no_position_no_fabrication(client):
    resp = await client.post(
        "/api/v1/seo/rankings/track",
        json={"keyword": "flat white", "url": "https://shop.example"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["history"] == []
    assert body["serp_source"] == "none"
    assert body["note"]


@pytest.mark.asyncio
async def test_rankings_drop_alert(client):
    base = {"keyword": "cold brew", "url": "https://shop.example"}
    await client.post("/api/v1/seo/rankings/track", json={**base, "position": 3})
    resp = await client.post("/api/v1/seo/rankings/track", json={**base, "position": 12})
    assert any("Dropped" in a for a in resp.json()["alerts"])  # 3 -> 12 is a 9-position drop

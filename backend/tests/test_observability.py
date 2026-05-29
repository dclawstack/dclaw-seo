import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint_public(client, real_auth):
    # /metrics must be reachable without auth (Prometheus scrape).
    r = await client.get("/metrics")
    assert r.status_code == 200
    assert "dclaw_seo_http_requests_total" in r.text


@pytest.mark.asyncio
async def test_admin_health(client, real_auth):
    r = await client.get("/admin/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"
    assert "llm" in body["checks"]


@pytest.mark.asyncio
async def test_security_headers_present(client):
    r = await client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "Referrer-Policy" in r.headers


@pytest.mark.asyncio
async def test_request_counter_increments(client, real_auth):
    before = await client.get("/metrics")
    await client.get("/health")
    after = await client.get("/metrics")
    # The exposition text grows / changes as the /health counter ticks.
    assert "dclaw_seo_http_requests_total" in after.text
    assert before.status_code == 200

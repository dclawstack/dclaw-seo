import pytest


@pytest.mark.asyncio
async def test_stats_reflect_real_activity(client):
    # empty baseline
    empty = (await client.get("/api/v1/seo/stats")).json()
    assert empty["audits"] == 0
    assert empty["recent"] == []

    # create real rows through the endpoints
    await client.post("/api/v1/seo/audit", json={"url": "https://example.com"})
    await client.post(
        "/api/v1/seo/content/optimize",
        json={"target_keyword": "espresso", "content": "Espresso is coffee."},
    )
    await client.post(
        "/api/v1/seo/rankings/track",
        json={"keyword": "latte", "url": "https://x.io", "position": 5},
    )

    stats = (await client.get("/api/v1/seo/stats")).json()
    assert stats["audits"] == 1
    assert stats["optimizations"] == 1
    assert stats["rank_observations"] == 1
    assert isinstance(stats["latest_audit_score"], int)
    assert len(stats["recent"]) == 3
    assert {a["type"] for a in stats["recent"]} == {"audit", "content", "ranking"}

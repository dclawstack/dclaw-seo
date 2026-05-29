import pytest

from app.services.performance import _recommendations, parse_psi

_SAMPLE = {
    "lighthouseResult": {
        "categories": {"performance": {"score": 0.85}},
        "audits": {
            "largest-contentful-paint": {"numericValue": 3200},
            "cumulative-layout-shift": {"numericValue": 0.05},
            "first-contentful-paint": {"numericValue": 1500},
            "total-blocking-time": {"numericValue": 350},
            "speed-index": {"numericValue": 4000},
        },
    }
}


def test_parse_psi_extracts_cwv():
    m = parse_psi(_SAMPLE)
    assert m["score"] == 85
    assert m["lcp_ms"] == 3200
    assert m["cls"] == 0.05
    assert m["tbt_ms"] == 350


def test_parse_psi_raises_on_error():
    with pytest.raises(ValueError):
        parse_psi({"error": {"message": "Quota exceeded"}})


def test_recommendations_from_metrics():
    recs = _recommendations(parse_psi(_SAMPLE))
    joined = " ".join(recs)
    assert "LCP" in joined  # 3200ms > 2500 -> flagged
    assert "Total Blocking Time" in joined  # 350ms > 200 -> flagged


@pytest.mark.asyncio
async def test_performance_history_empty(client):
    resp = await client.get("/api/v1/seo/performance", params={"url": "https://none.test"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["history"] == []
    assert body["score"] is None

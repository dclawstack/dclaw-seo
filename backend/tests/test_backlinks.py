import pytest

from app.core.config import settings
from app.services.backlinks import heuristic_toxicity


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_heuristic_flags_spam():
    score, reasons = heuristic_toxicity("http://cheap-casino.xyz/p", "buy now casino")
    assert score >= 60
    assert any("TLD" in r for r in reasons)


def test_heuristic_clean_link_low_score():
    score, _ = heuristic_toxicity("https://www.nytimes.com/article", "great guide")
    assert score < 60


@pytest.mark.asyncio
async def test_backlink_analyze_and_new_lost(client, no_llm):
    target = "https://mysite.com"
    payload = {
        "target_url": target,
        "links": [
            {"source_url": "https://goodblog.com/post", "anchor_text": "useful resource"},
            {"source_url": "http://spam.xyz/x", "anchor_text": "cheap casino loan"},
        ],
    }
    r1 = await client.post("/api/v1/seo/backlinks/analyze", json=payload)
    assert r1.status_code == 200
    b1 = r1.json()
    assert b1["total"] == 2
    assert b1["new_count"] == 2
    assert b1["toxic_count"] >= 1
    assert b1["llm_enriched"] is False
    assert b1["note"]

    # Re-analyze with only the clean link -> the spam link becomes "lost".
    r2 = await client.post(
        "/api/v1/seo/backlinks/analyze",
        json={"target_url": target, "links": [payload["links"][0]]},
    )
    b2 = r2.json()
    assert b2["new_count"] == 0
    assert b2["lost_count"] == 1
    lost = [x for x in b2["backlinks"] if x["status"] == "lost"]
    assert lost and lost[0]["source_url"] == "http://spam.xyz/x"


@pytest.mark.asyncio
async def test_backlinks_list(client, no_llm):
    target = "https://listme.com"
    await client.post(
        "/api/v1/seo/backlinks/analyze",
        json={"target_url": target, "links": [{"source_url": "https://a.com/1"}]},
    )
    r = await client.get("/api/v1/seo/backlinks", params={"target_url": target})
    assert r.status_code == 200
    assert r.json()["total"] == 1

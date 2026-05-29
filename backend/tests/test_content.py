import pytest

from app.core.config import settings
from app.services.content_optimizer import analyze


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_analyze_computes_real_metrics():
    text = "Coffee is great. Coffee lovers enjoy coffee daily. We drink coffee."
    m = analyze(text, "coffee")
    assert m["word_count"] == 11
    assert m["occurrences"] == 4
    assert m["keyword_density"] == pytest.approx(100 * 4 / 11, abs=0.1)
    assert 0 <= m["readability"] <= 100
    assert m["keyword_in_intro"] is True


@pytest.mark.asyncio
async def test_optimize_endpoint_scores_without_llm(client, no_llm):
    body_text = "This is a short article about espresso. Espresso is strong coffee."
    resp = await client.post(
        "/api/v1/seo/content/optimize",
        json={"target_keyword": "espresso", "content": body_text},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_keyword"] == "espresso"
    assert isinstance(data["score"], int) and 0 <= data["score"] <= 100
    assert data["word_count"] > 0
    assert data["llm_enriched"] is False
    assert data["optimized_content"] is None  # no rewrite without an LLM
    assert len(data["suggestions"]) >= 5
    assert data["note"]


@pytest.mark.asyncio
async def test_optimize_rejects_empty(client):
    resp = await client.post(
        "/api/v1/seo/content/optimize",
        json={"target_keyword": "", "content": ""},
    )
    assert resp.status_code == 422

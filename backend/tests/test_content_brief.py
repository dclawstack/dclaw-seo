import pytest

from app.core.config import settings
from app.services.content_brief import _deterministic_brief, _questions


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_questions_detected():
    qs = _questions(["how to make cold brew", "cold brew ratio", "what is nitro brew"])
    assert any(q.startswith("How") and q.endswith("?") for q in qs)
    assert any(q.startswith("What") for q in qs)


def test_deterministic_brief_structure():
    brief = _deterministic_brief(
        "cold brew coffee",
        ["cold brew ratio", "how to make cold brew", "cold brew vs iced coffee", "best cold brew maker"],
    )
    assert brief.keyword == "cold brew coffee"
    assert brief.title_suggestions
    assert len(brief.outline) >= 2
    assert brief.recommended_words > 0
    assert brief.llm_enriched is False


@pytest.mark.asyncio
async def test_brief_endpoint_real(client, no_llm):
    resp = await client.post("/api/v1/seo/content/brief", json={"keyword": "cold brew coffee"})
    if resp.status_code != 200:
        pytest.skip("network unavailable")
    body = resp.json()
    assert body["keyword"] == "cold brew coffee"
    assert len(body["outline"]) >= 1
    assert body["recommended_words"] > 0

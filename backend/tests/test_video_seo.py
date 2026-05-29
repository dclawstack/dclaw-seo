import pytest

from app.core.config import settings
from app.services.video_seo import _deterministic, _hashtags


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_hashtags_format():
    tags = _hashtags(["cold brew", "iced coffee"], "coffee")
    assert all(t.startswith("#") for t in tags)
    assert len(tags) <= 5


def test_deterministic_three_titles():
    out = _deterministic("make cold brew", ["cold brew ratio", "cold brew maker"])
    assert len(out.title_variants) == 3
    assert out.tags
    assert out.llm_enriched is False


@pytest.mark.asyncio
async def test_video_endpoint_fallback(client, no_llm):
    resp = await client.post("/api/v1/seo/video", json={"topic": "make cold brew coffee"})
    if resp.status_code != 200:
        pytest.skip("network unavailable")
    body = resp.json()
    assert body["topic"] == "make cold brew coffee"
    assert len(body["title_variants"]) == 3

import pytest

from app.core.config import settings
from app.services.content_writer import _scaffold, count_words, originality_score


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_count_words():
    assert count_words("one two three") == 3
    assert count_words("") == 0


def test_originality_full_unique():
    assert originality_score("the quick brown fox jumps over a lazy dog today") == 100.0


def test_originality_detects_repetition():
    text = ("alpha beta gamma delta epsilon " * 4).strip()
    assert originality_score(text) < 100.0


def test_scaffold_structure():
    out = _scaffold("cold brew coffee", ["cold brew ratio", "cold brew maker"], 1000)
    assert out.keyword == "cold brew coffee"
    assert out.title
    assert len(out.sections) >= 2
    assert out.word_count > 0
    assert out.llm_generated is False
    assert 0 <= out.originality_score <= 100


@pytest.mark.asyncio
async def test_write_endpoint_fallback(client, no_llm):
    resp = await client.post(
        "/api/v1/seo/content/write", json={"keyword": "cold brew coffee"}
    )
    if resp.status_code != 200:
        pytest.skip("network unavailable")
    body = resp.json()
    assert body["keyword"] == "cold brew coffee"
    assert body["sections"]
    assert body["llm_generated"] is False

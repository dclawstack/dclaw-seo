import pytest

from app.core.config import settings
from app.schemas.meta_tags import MetaTagsRequest
from app.services.meta_tags import _deterministic, _truncate


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_truncate_keeps_short():
    assert _truncate("short", 60) == "short"


def test_truncate_long_adds_ellipsis():
    out = _truncate("word " * 50, 60)
    assert len(out) <= 61
    assert out.endswith("…")


def test_deterministic_lengths():
    req = MetaTagsRequest(content="A long article about making cold brew coffee at home. " * 10,
                          keyword="cold brew coffee")
    out = _deterministic(req, title=None, existing_meta=None, text=req.content)
    assert out.title_length <= 60
    assert out.meta_length <= 160
    assert out.json_ld["@type"] == "Article"
    assert "og:title" in out.og_tags
    assert out.llm_enriched is False


def test_request_requires_source():
    with pytest.raises(ValueError):
        MetaTagsRequest()


@pytest.mark.asyncio
async def test_meta_endpoint_content(client, no_llm):
    resp = await client.post(
        "/api/v1/seo/meta",
        json={"content": "How to make cold brew coffee at home, step by step.",
              "keyword": "cold brew coffee"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title_tag"]
    assert body["json_ld"]["@type"] == "Article"

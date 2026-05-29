import pytest

from app.core.config import settings
from app.services import seo_data
from app.services.seo_data import GoogleSuggestProvider, ProviderUnavailable


class _FakeProvider:
    """Deterministic in-test keyword source (stands in for the external API)."""

    def __init__(self, terms):
        self._terms = terms

    async def expand(self, seed: str, target: int = 50):
        return self._terms[:target]


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


@pytest.fixture
def fake_keyword_provider(monkeypatch):
    fake = _FakeProvider(["coffee beans", "best coffee grinder", "coffee near me"])
    monkeypatch.setattr(seo_data, "keyword_provider", fake)
    return fake


@pytest.mark.asyncio
async def test_keywords_returns_real_suggestions_without_llm(client, no_llm, fake_keyword_provider):
    resp = await client.post("/api/v1/seo/keywords", json={"seed": "coffee"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["seed"] == "coffee"
    assert [s["term"] for s in body["suggestions"]] == [
        "coffee beans",
        "best coffee grinder",
        "coffee near me",
    ]
    # No LLM configured -> no fabricated metrics, just real suggestions + a note.
    assert body["llm_enriched"] is False
    assert body["note"]
    for s in body["suggestions"]:
        assert s["volume_band"] is None
        assert s["difficulty_band"] is None
        assert s["intent"] is None


@pytest.mark.asyncio
async def test_keywords_rejects_empty_seed(client):
    resp = await client.post("/api/v1/seo/keywords", json={"seed": ""})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_google_suggest_provider_real(client):
    """Integration: hits the real (free, keyless) Google Suggest endpoint."""
    try:
        terms = await GoogleSuggestProvider().expand("coffee", target=20)
    except ProviderUnavailable:
        pytest.skip("Google Suggest not reachable in this environment")
    assert len(terms) >= 5
    assert all(isinstance(t, str) and t for t in terms)

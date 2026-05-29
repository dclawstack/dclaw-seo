import pytest

from app.core.config import settings
from app.services import copilot
from app.services.copilot import PageFetchError, analyze_page, extract_signals

_HTML = """
<html><head>
<title>Best Espresso Machines for Home Baristas in 2026</title>
<meta name="description" content="A short meta.">
</head><body>
<h1>Espresso Machines</h1>
<p>Espresso is a concentrated coffee. Baristas love espresso. This guide covers espresso machines for the home.</p>
<script>var x = 1;</script>
</body></html>
"""


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_extract_signals_real_parsing():
    s = extract_signals(_HTML)
    assert s.title == "Best Espresso Machines for Home Baristas in 2026"
    assert s.title_length == len(s.title)
    assert s.meta_description == "A short meta."
    assert s.h1_count == 1
    assert s.word_count > 0
    assert "var x" not in (s.title or "")  # script content stripped


@pytest.mark.asyncio
async def test_copilot_endpoint_with_injected_page(client, no_llm, monkeypatch):
    async def fake_fetch(url: str) -> str:
        return _HTML

    monkeypatch.setattr(copilot, "_default_fetch", fake_fetch)
    resp = await client.post("/api/v1/ai/copilot", json={"url": "https://example.com/espresso"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["url"] == "https://example.com/espresso"
    assert body["llm_enriched"] is False
    assert body["note"]
    assert len(body["actions"]) >= 1
    # short meta (< 140) should surface a meta action
    cats = {a["category"] for a in body["actions"]}
    assert "meta" in cats
    # actions are priority-sorted
    prios = [a["priority"] for a in body["actions"]]
    assert prios == sorted(prios)


@pytest.mark.asyncio
async def test_copilot_fetch_error_returns_502(client, monkeypatch):
    async def boom(url: str) -> str:
        raise PageFetchError("nope")

    monkeypatch.setattr(copilot, "_default_fetch", boom)
    resp = await client.post("/api/v1/ai/copilot", json={"url": "https://unreachable.invalid"})
    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_copilot_real_fetch_example_com():
    """Integration: fetch a real, stable page."""
    try:
        result = await analyze_page("https://example.com")
    except PageFetchError:
        pytest.skip("example.com not reachable in this environment")
    assert result.signals.title
    assert len(result.actions) >= 1

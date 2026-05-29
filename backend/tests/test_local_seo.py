import pytest

from app.core.config import settings
from app.services.local_seo import norm_address, norm_name, norm_phone


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def test_norm_name_strips_suffix():
    assert norm_name("Joe's Coffee, LLC") == norm_name("Joes Coffee")


def test_norm_phone_last10():
    assert norm_phone("+1 (415) 555-0123") == "4155550123"
    assert norm_phone("415.555.0123") == "4155550123"


def test_norm_address_abbreviations():
    assert norm_address("123 Main Street") == norm_address("123 Main St")


@pytest.mark.asyncio
async def test_local_seo_flow(client, no_llm):
    # create business
    r = await client.post(
        "/api/v1/local/businesses",
        json={"name": "Joe's Coffee", "address": "123 Main St", "phone": "415-555-0123"},
    )
    assert r.status_code == 200
    biz = r.json()["business"]
    bid = biz["id"]
    assert r.json()["synced_from_gbp"] is False

    # consistent citation
    r = await client.post(
        f"/api/v1/local/businesses/{bid}/citations",
        json={"source": "yelp", "listed_name": "Joe's Coffee LLC",
              "listed_address": "123 Main Street", "listed_phone": "(415) 555-0123"},
    )
    assert r.status_code == 200
    assert r.json()["nap_consistent"] is True

    # inconsistent citation (wrong phone)
    r = await client.post(
        f"/api/v1/local/businesses/{bid}/citations",
        json={"source": "yellowpages", "listed_name": "Joe's Coffee",
              "listed_address": "123 Main St", "listed_phone": "415-555-9999"},
    )
    assert r.json()["nap_consistent"] is False
    assert "phone" in r.json()["mismatch_fields"]

    # nap scan
    r = await client.get(f"/api/v1/local/businesses/{bid}/nap-scan")
    body = r.json()
    assert body["total_citations"] == 2
    assert body["consistent"] == 1
    assert body["inconsistent"] == 1
    assert body["consistency_score"] == 50.0

    # review with AI/template response
    r = await client.post(
        f"/api/v1/local/businesses/{bid}/reviews",
        json={"source": "google", "author": "Sam", "rating": 2, "text": "Slow service"},
    )
    assert r.status_code == 200
    assert r.json()["suggested_response"]
    assert r.json()["rating"] == 2


@pytest.mark.asyncio
async def test_citation_unknown_business(client):
    r = await client.post(
        "/api/v1/local/businesses/99999/citations",
        json={"source": "yelp", "listed_name": "X", "listed_address": "Y", "listed_phone": "1"},
    )
    assert r.status_code == 404

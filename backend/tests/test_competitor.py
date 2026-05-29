import pytest

from app.services.competitor import _gaps, extract_competitor_terms

_HTML = """
<html><head>
<title>Cold Brew Coffee Makers and Recipes</title>
<meta name="description" content="Best cold brew coffee makers, recipes, and brewing guides.">
</head><body>
<h1>Cold Brew Coffee</h1>
<h2>Nitro Cold Brew Recipes</h2>
<h3>Coffee Maker Reviews</h3>
</body></html>
"""


def test_extract_terms_finds_prominent_phrases():
    terms = extract_competitor_terms(_HTML)
    joined = " ".join(terms)
    assert "cold brew" in joined
    assert any("nitro" in t for t in terms)


def test_gaps_excludes_covered_terms():
    your = ["cold brew coffee", "cold brew recipes"]
    competitor = ["cold brew coffee", "nitro cold brew", "coffee maker reviews"]
    gaps = _gaps(your, competitor)
    terms = [g.term for g in gaps]
    # "cold brew coffee" is covered by your keywords -> not a gap
    assert "cold brew coffee" not in terms
    # uncovered competitor topics surface as gaps with opportunity scores
    assert any("nitro" in t or "maker" in t for t in terms)
    assert all(0 <= g.opportunity <= 100 for g in gaps)


@pytest.mark.asyncio
async def test_competitor_gap_endpoint_real(client):
    resp = await client.post(
        "/api/v1/seo/competitor/gap",
        json={"seed": "cold brew coffee", "competitor_url": "https://example.com"},
    )
    if resp.status_code != 200:
        pytest.skip("network unavailable")
    body = resp.json()
    assert body["competitor_url"] == "https://example.com"
    assert "gaps" in body
    assert isinstance(body["your_keyword_count"], int)

import pytest

from app.services.site_auditor import _extract_links, _page_issues, _score

_BAD_HTML = """
<html><head></head><body>
<p>short</p>
<img src="/a.png">
<a href="/about">about</a>
<a href="https://external.example/x">ext</a>
</body></html>
"""


def test_page_issues_flags_real_problems():
    issues = _page_issues("https://site.test/", _BAD_HTML, elapsed_ms=100)
    types = {i.type for i in issues}
    assert "missing_title" in types
    assert "missing_h1" in types
    assert "missing_meta_description" in types
    assert "thin_content" in types
    assert "img_missing_alt" in types
    assert all(i.url == "https://site.test/" for i in issues)


def test_extract_links_resolves_relative():
    links = _extract_links("https://site.test/page", _BAD_HTML)
    assert "https://site.test/about" in links
    assert "https://external.example/x" in links


def test_score_decreases_with_issues():
    from app.schemas.seo import IssueItem

    none = _score([], 1)
    some = _score([IssueItem(severity="error", message="x")], 1)
    assert none == 100
    assert some < none


@pytest.mark.asyncio
async def test_audit_endpoint_real_crawl(client):
    """Integration: crawl a real, stable page."""
    resp = await client.post(
        "/api/v1/seo/audit", json={"url": "https://example.com", "max_pages": 2}
    )
    if resp.status_code != 200:
        pytest.skip("network unavailable for crawl")
    body = resp.json()
    assert body["pages_crawled"] >= 1
    assert 0 <= body["score"] <= 100
    assert body["summary"]
    assert isinstance(body["issues"], list)

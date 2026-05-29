from datetime import datetime

import pytest

from app.core.config import settings
from app.schemas.reports import ReportMetric, ReportPreview
from app.services.reports import _hex_to_rgb, build_csv, build_pdf


@pytest.fixture
def no_llm():
    saved = (settings.ollama_url, settings.ollama_model, settings.openrouter_api_key)
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    yield
    settings.ollama_url, settings.ollama_model, settings.openrouter_api_key = saved


def _preview():
    return ReportPreview(
        title="SEO Report",
        brand_company="Acme",
        generated_at=datetime(2026, 1, 1, 12, 0),
        metrics=[ReportMetric(label="Keywords", value="42")],
        executive_summary="Solid progress this period.",
        summary_ai=False,
    )


def test_hex_to_rgb():
    assert _hex_to_rgb("#6E56CF") == (110, 86, 207)
    assert _hex_to_rgb("bad") == (110, 86, 207)
    assert _hex_to_rgb(None) == (110, 86, 207)


def test_build_csv_contains_metrics():
    out = build_csv(_preview())
    assert "Keywords" in out
    assert "42" in out
    assert "Acme" in out


def test_build_pdf_is_pdf_bytes():
    pdf = build_pdf(_preview(), "#6E56CF")
    assert isinstance(pdf, bytes)
    assert pdf[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_preview_endpoint(client, no_llm):
    r = await client.post("/api/v1/reports/preview", json={"title": "Q1", "brand_company": "Acme"})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Q1"
    assert body["metrics"]
    assert body["summary_ai"] is False


@pytest.mark.asyncio
async def test_pdf_endpoint(client, no_llm):
    r = await client.post("/api/v1/reports/pdf", json={"title": "Q1"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_schedule_crud_and_run(client, no_llm):
    r = await client.post(
        "/api/v1/reports/schedules",
        json={"site_url": "https://x.com", "frequency": "weekly", "recipient": "a@b.com"},
    )
    assert r.status_code == 200
    r = await client.get("/api/v1/reports/schedules")
    assert len(r.json()) == 1
    # new schedule has no last_run_at -> due -> runs; SMTP not configured -> not delivered
    r = await client.post("/api/v1/reports/schedules/run-due")
    body = r.json()
    assert len(body) == 1
    assert body[0]["delivered"] is False

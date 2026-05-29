from datetime import datetime, timedelta

import pytest

from app.models.ranking import Ranking
from app.schemas.forecast import ForecastRequest
from app.services.forecast import _ols, forecast_from_history


def _rows(positions, competitor=None):
    base = datetime(2026, 1, 1)
    rows = []
    for i, p in enumerate(positions):
        rows.append(
            Ranking(
                keyword="k",
                url="u",
                position=p,
                competitor_position=(competitor[i] if competitor else None),
                tracked_at=base + timedelta(days=i),
            )
        )
    return rows


def test_ols_perfect_line():
    slope, intercept, r2 = _ols([0, 1, 2, 3], [10, 8, 6, 4])
    assert round(slope, 3) == -2.0
    assert round(r2, 3) == 1.0


def test_insufficient_data():
    out = forecast_from_history(_rows([5]), ForecastRequest(keyword="k", url="u"))
    assert out.trend == "insufficient_data"
    assert out.confidence == "none"
    assert out.forecast == []


def test_improving_trend_projects_better():
    out = forecast_from_history(
        _rows([10, 9, 8, 7, 6]), ForecastRequest(keyword="k", url="u", horizon=3)
    )
    assert out.trend == "improving"
    assert len(out.forecast) == 3
    # projected positions keep dropping (improving), bounded at >= 1
    assert out.forecast[-1].position <= out.current_position


def test_rank_floor_at_one():
    out = forecast_from_history(
        _rows([3, 2, 1, 1]), ForecastRequest(keyword="k", url="u", horizon=5)
    )
    assert all(p.position >= 1.0 for p in out.forecast)


def test_competitor_pressure_detected():
    out = forecast_from_history(
        _rows([5, 5, 5, 5], competitor=[10, 8, 6, 4]),
        ForecastRequest(keyword="k", url="u"),
    )
    assert out.competitor_pressure == "gaining"


@pytest.mark.asyncio
async def test_forecast_endpoint_empty(client):
    r = await client.post(
        "/api/v1/reports/forecast", json={"keyword": "nope", "url": "https://x.com"}
    )
    assert r.status_code == 200
    assert r.json()["trend"] == "insufficient_data"

"""Predictive rank forecasting.

Projects future search positions for a keyword/URL from its **real** stored rank
history (`rankings` table) using ordinary least-squares on (check index →
position), then adjusts for competitor movement recorded alongside each check.

Honest by construction: with fewer than 2 observations there is nothing to fit,
so we return ``trend=insufficient_data`` instead of inventing a number.
Confidence is derived from the sample size and the fit's R², never asserted.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ranking import Ranking
from app.repositories.ranking import RankingRepository
from app.schemas.forecast import ForecastPoint, ForecastRequest, ForecastResponse


def _ols(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Return (slope, intercept, r_squared) for y ~ x."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return 0.0, my, 0.0
    slope = sxy / sxx
    intercept = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return slope, intercept, r2


def _confidence(n: int, r2: float) -> str:
    if n >= 8 and r2 >= 0.6:
        return "high"
    if n >= 4 and r2 >= 0.3:
        return "medium"
    return "low"


def _competitor_pressure(rows: Sequence[Ranking]) -> str | None:
    comp = [(i, r.competitor_position) for i, r in enumerate(rows) if r.competitor_position is not None]
    if len(comp) < 2:
        return None
    xs = [float(i) for i, _ in comp]
    ys = [float(p) for _, p in comp]
    slope, _, _ = _ols(xs, ys)
    if slope < -0.3:
        return "gaining"  # competitor's rank improving (number dropping)
    if slope > 0.3:
        return "easing"
    return "stable"


def forecast_from_history(rows: Sequence[Ranking], request: ForecastRequest) -> ForecastResponse:
    positions = [(i, r.position) for i, r in enumerate(rows) if r.position is not None]
    n = len(positions)
    if n < 2:
        return ForecastResponse(
            keyword=request.keyword,
            url=request.url,
            data_points=n,
            current_position=float(positions[-1][1]) if positions else None,
            trend="insufficient_data",
            confidence="none",
            note=(
                "Need at least 2 recorded rank checks to forecast. Track this keyword over "
                "time (Rankings) and the forecast will populate."
            ),
        )
    xs = [float(i) for i, _ in positions]
    ys = [float(p) for _, p in positions]
    slope, intercept, r2 = _ols(xs, ys)
    last_x = xs[-1]
    current = ys[-1]

    pressure = _competitor_pressure(rows)
    # Competitor gaining puts upward (worsening) pressure on our projection.
    adjust = 0.0
    if pressure == "gaining":
        adjust = 0.25
    elif pressure == "easing":
        adjust = -0.25

    forecast: list[ForecastPoint] = []
    for step in range(1, request.horizon + 1):
        raw = slope * (last_x + step) + intercept + adjust * step
        projected = max(1.0, round(raw, 1))  # rank can't be < 1
        forecast.append(ForecastPoint(step=step, position=projected))

    if slope < -0.2:
        trend = "improving"
    elif slope > 0.2:
        trend = "declining"
    else:
        trend = "stable"

    return ForecastResponse(
        keyword=request.keyword,
        url=request.url,
        data_points=n,
        current_position=round(current, 1),
        slope_per_check=round(slope, 3),
        trend=trend,
        confidence=_confidence(n, r2),
        competitor_pressure=pressure,
        forecast=forecast,
        note=(
            "Forecast from a least-squares fit on your real rank history; competitor movement "
            "(when recorded) nudges the projection. Lower position = better."
        ),
    )


async def forecast_rank(db: AsyncSession, request: ForecastRequest) -> ForecastResponse:
    rows = await RankingRepository(db).history(request.keyword, request.url, limit=60)
    return forecast_from_history(rows, request)

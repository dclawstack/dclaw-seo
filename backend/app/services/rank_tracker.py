"""Rank tracking & SERP monitoring.

Records real rank observations (from a configured SERP provider or a manually
supplied position — never fabricated), returns the stored trend history, and
flags anomalies when a keyword drops more than five positions between
consecutive observations.
"""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ranking import Ranking
from app.repositories.ranking import RankingRepository
from app.schemas.seo import RankDataPoint, RankingsTrackRequest, RankingsTrackResponse
from app.services import serp as serp_module

DROP_THRESHOLD = 5


def _detect_alerts(rows: Sequence[Ranking]) -> list[str]:
    alerts: list[str] = []
    for prev, cur in zip(rows, rows[1:]):
        if prev.position is None or cur.position is None:
            continue
        # Larger position number = worse rank; a positive delta is a drop.
        delta = cur.position - prev.position
        if delta > DROP_THRESHOLD:
            alerts.append(
                f"Dropped {delta} positions ({prev.position} → {cur.position}) on "
                f"{cur.tracked_at.strftime('%Y-%m-%d')}."
            )
    return alerts


async def track_rankings(
    db: AsyncSession,
    request: RankingsTrackRequest,
    provider: serp_module.SERPProvider | None = None,
) -> RankingsTrackResponse:
    provider = provider or serp_module.serp_provider
    repo = RankingRepository(db)

    position = await provider.position(request.keyword, request.url)
    source = provider.name
    if position is None and request.position is not None:
        position = request.position
        source = "manual"

    note: str | None = None
    if position is not None:
        await repo.create(
            Ranking(keyword=request.keyword, url=request.url, position=position)
        )
    else:
        note = (
            "No position recorded — supply `position` (a real observed rank) or configure a "
            "SERP provider. Showing previously stored history."
        )

    rows = await repo.history(request.keyword, request.url)
    history = [
        RankDataPoint(
            date=r.tracked_at.strftime("%Y-%m-%d"),
            position=r.position,
            competitor_position=r.competitor_position,
        )
        for r in rows
        if r.position is not None
    ]
    return RankingsTrackResponse(
        keyword=request.keyword,
        url=request.url,
        history=history,
        alerts=_detect_alerts(rows),
        serp_source=source,
        note=note,
    )

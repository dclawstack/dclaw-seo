from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.forecast import ForecastRequest, ForecastResponse
from app.schemas.reports import (
    ReportPreview,
    ReportRequest,
    ScheduleCreate,
    ScheduleOut,
    ScheduleRunResult,
)
from app.services import reports as svc
from app.services.forecast import forecast_rank

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/preview", response_model=ReportPreview)
async def report_preview(
    request: ReportRequest, db: AsyncSession = Depends(get_db)
) -> ReportPreview:
    """Build the report data + AI executive summary (no file)."""
    return await svc.build_preview(db, request)


@router.post("/pdf")
async def report_pdf(request: ReportRequest, db: AsyncSession = Depends(get_db)) -> Response:
    """Branded PDF report."""
    preview = await svc.build_preview(db, request)
    pdf = svc.build_pdf(preview, request.brand_color)
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="seo-report.pdf"'},
    )


@router.post("/csv")
async def report_csv(request: ReportRequest, db: AsyncSession = Depends(get_db)) -> Response:
    """CSV export of the report metrics + summary."""
    preview = await svc.build_preview(db, request)
    return Response(
        content=svc.build_csv(preview),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="seo-report.csv"'},
    )


@router.post("/schedules", response_model=ScheduleOut)
async def create_schedule(
    payload: ScheduleCreate, db: AsyncSession = Depends(get_db)
) -> ScheduleOut:
    sched = await svc.create_schedule(db, payload)
    return ScheduleOut.model_validate(sched)


@router.get("/schedules", response_model=list[ScheduleOut])
async def list_schedules(db: AsyncSession = Depends(get_db)) -> list[ScheduleOut]:
    rows = await svc.list_schedules(db)
    return [ScheduleOut.model_validate(r) for r in rows]


@router.post("/schedules/run-due", response_model=list[ScheduleRunResult])
async def run_due(db: AsyncSession = Depends(get_db)) -> list[ScheduleRunResult]:
    """Generate + deliver every due scheduled report (cron hook)."""
    return await svc.run_due_schedules(db)


@router.post("/forecast", response_model=ForecastResponse)
async def forecast(request: ForecastRequest, db: AsyncSession = Depends(get_db)) -> ForecastResponse:
    """Predictive rank forecast from stored rank history + competitor movement."""
    return await forecast_rank(db, request)

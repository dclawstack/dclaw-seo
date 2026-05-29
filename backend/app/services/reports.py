"""White-label SEO reports.

Builds a branded report (PDF via fpdf2, or CSV) from the account's **real**
dashboard aggregates, with an AI-written executive summary (LLM, deterministic
fallback). Supports stored delivery schedules; actual email send is wired behind
SMTP_* env and degrades gracefully (the report is still generated) when SMTP is
not configured — it never claims a delivery that didn't happen.
"""

from __future__ import annotations

import csv
import io
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

from fpdf import FPDF
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.report_schedule import ReportSchedule
from app.repositories.report_schedule import ReportScheduleRepository
from app.schemas.reports import (
    ReportMetric,
    ReportPreview,
    ReportRequest,
    ScheduleCreate,
    ScheduleRunResult,
)
from app.services.llm import LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config
from app.services.stats import dashboard_stats

logger = get_logger(__name__)

_DEFAULT_COLOR = (110, 86, 207)  # DKube purple #6E56CF


def _hex_to_rgb(value: str | None) -> tuple[int, int, int]:
    if not value:
        return _DEFAULT_COLOR
    v = value.lstrip("#")
    if len(v) != 6:
        return _DEFAULT_COLOR
    try:
        return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)
    except ValueError:
        return _DEFAULT_COLOR


async def _metrics(db: AsyncSession) -> list[ReportMetric]:
    stats = await dashboard_stats(db)
    return [
        ReportMetric(label="Site audits run", value=str(stats.audits)),
        ReportMetric(label="Keywords researched", value=str(stats.keywords)),
        ReportMetric(label="Content optimizations", value=str(stats.optimizations)),
        ReportMetric(label="Rank observations", value=str(stats.rank_observations)),
        ReportMetric(
            label="Latest audit score",
            value=str(stats.latest_audit_score) if stats.latest_audit_score is not None else "N/A",
        ),
    ]


def _deterministic_summary(metrics: list[ReportMetric], company: str | None) -> str:
    who = company or "your site"
    by = {m.label: m.value for m in metrics}
    return (
        f"This report summarizes SEO activity for {who}. To date we have run "
        f"{by.get('Site audits run', '0')} site audits, researched "
        f"{by.get('Keywords researched', '0')} keywords, and recorded "
        f"{by.get('Rank observations', '0')} rank observations. Continue tracking target "
        "keywords and acting on audit findings to compound visibility gains."
    )


_SYSTEM = (
    "You are an SEO consultant writing the executive summary of a client report. Given the "
    "metrics, write 3-4 concise, professional sentences highlighting progress and the top "
    "recommended next step. Return ONLY the summary prose."
)


async def _exec_summary(
    db: AsyncSession, metrics: list[ReportMetric], company: str | None
) -> tuple[str, bool]:
    cfg = await get_effective_config(db)
    payload = "\n".join(f"{m.label}: {m.value}" for m in metrics)
    try:
        raw = await llm_service.complete(
            [
                Message(role="system", content=_SYSTEM),
                Message(role="user", content=f"Company: {company or 'N/A'}\n{payload}"),
            ],
            config=cfg,
            temperature=0.4,
        )
    except LLMNotConfigured:
        return _deterministic_summary(metrics, company), False
    except LLMError as exc:
        logger.warning("report_llm_failed", error=str(exc))
        return _deterministic_summary(metrics, company), False
    cleaned = raw.strip()
    return (cleaned or _deterministic_summary(metrics, company)), bool(cleaned)


async def build_preview(db: AsyncSession, request: ReportRequest) -> ReportPreview:
    metrics = await _metrics(db)
    summary, ai = await _exec_summary(db, metrics, request.brand_company)
    return ReportPreview(
        title=request.title,
        brand_company=request.brand_company,
        generated_at=datetime.utcnow(),
        metrics=metrics,
        executive_summary=summary,
        summary_ai=ai,
        note=None if ai else "Executive summary is templated (no LLM configured).",
    )


def build_csv(preview: ReportPreview) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["DClaw SEO Report", preview.title])
    if preview.brand_company:
        w.writerow(["Prepared for", preview.brand_company])
    w.writerow(["Generated", preview.generated_at.isoformat()])
    w.writerow([])
    w.writerow(["Metric", "Value"])
    for m in preview.metrics:
        w.writerow([m.label, m.value])
    w.writerow([])
    w.writerow(["Executive summary", preview.executive_summary])
    return buf.getvalue()


def _safe(text: str) -> str:
    """The core PDF fonts are latin-1 only; replace anything outside it."""
    return text.encode("latin-1", "replace").decode("latin-1")


def build_pdf(preview: ReportPreview, brand_color: str | None) -> bytes:
    r, g, b = _hex_to_rgb(brand_color)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(r, g, b)
    pdf.rect(0, 0, 210, 28, "F")
    pdf.set_xy(12, 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, _safe(preview.title), ln=1)
    pdf.set_x(12)
    pdf.set_font("Helvetica", "", 10)
    sub = preview.brand_company or "DClaw SEO"
    pdf.cell(0, 6, _safe(f"Prepared for {sub}"), ln=1)

    pdf.ln(18)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Generated {preview.generated_at.strftime('%Y-%m-%d %H:%M UTC')}", ln=1)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 8, "Key Metrics", ln=1)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 11)
    for m in preview.metrics:
        pdf.cell(120, 8, _safe(m.label), border="B")
        pdf.cell(0, 8, _safe(m.value), border="B", ln=1)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 8, "Executive Summary", ln=1)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, _safe(preview.executive_summary))

    out = pdf.output()
    return bytes(out)


# --- Schedules ----------------------------------------------------------------

async def create_schedule(db: AsyncSession, payload: ScheduleCreate) -> ReportSchedule:
    sched = ReportSchedule(
        site_url=payload.site_url,
        frequency=payload.frequency,
        recipient=payload.recipient,
        brand_company=payload.brand_company,
        brand_color=payload.brand_color,
    )
    return await ReportScheduleRepository(db).create(sched)


async def list_schedules(db: AsyncSession):
    return await ReportScheduleRepository(db).list()


_INTERVAL = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1), "monthly": timedelta(days=30)}


def _is_due(sched: ReportSchedule, now: datetime) -> bool:
    if sched.last_run_at is None:
        return True
    return now - sched.last_run_at >= _INTERVAL.get(sched.frequency, timedelta(weeks=1))


def _deliver_email(recipient: str, subject: str, body: str, pdf: bytes) -> tuple[bool, str]:
    if not settings.smtp_host:
        return False, "SMTP not configured (SMTP_HOST) — report generated but not emailed."
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    msg.add_attachment(pdf, maintype="application", subtype="pdf", filename="seo-report.pdf")
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as s:
            s.starttls()
            if settings.smtp_user:
                s.login(settings.smtp_user, settings.smtp_password)
            s.send_message(msg)
        return True, f"Emailed to {recipient}."
    except Exception as exc:  # delivery failures must not crash the run
        logger.warning("report_email_failed", error=str(exc))
        return False, f"SMTP send failed: {exc}"


async def run_due_schedules(db: AsyncSession, now: datetime | None = None) -> list[ScheduleRunResult]:
    now = now or datetime.utcnow()
    repo = ReportScheduleRepository(db)
    schedules = list(await repo.list())
    results: list[ScheduleRunResult] = []
    for sched in schedules:
        if not _is_due(sched, now):
            continue
        request = ReportRequest(
            title="SEO Performance Report",
            brand_company=sched.brand_company,
            brand_color=sched.brand_color,
            site_url=sched.site_url,
        )
        preview = await build_preview(db, request)
        pdf = build_pdf(preview, sched.brand_color)
        delivered, detail = _deliver_email(
            sched.recipient, preview.title, preview.executive_summary, pdf
        )
        sched.last_run_at = now
        results.append(
            ScheduleRunResult(
                schedule_id=sched.id, recipient=sched.recipient, delivered=delivered, detail=detail
            )
        )
    if results:
        await db.commit()
    return results

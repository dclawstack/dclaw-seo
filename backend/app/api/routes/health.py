from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.observability import metrics_payload
from app.services.llm import LLMConfig
from app.services.llm_config import get_effective_config

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Liveness check."""
    return {"status": "ok", "version": settings.app_version}


@router.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics exposition."""
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)


@router.get("/admin/health")
async def admin_health(db: AsyncSession = Depends(get_db)) -> dict:
    """Readiness check: database connectivity + LLM configuration."""
    checks: dict = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # surface, don't crash the probe
        checks["database"] = f"error: {exc}"

    try:
        cfg: LLMConfig = await get_effective_config(db)
        configured = [p for p in cfg.provider_order() if cfg.is_configured(p)]
        checks["llm"] = {"configured_providers": configured, "provider_order": cfg.provider_order()}
    except Exception as exc:
        checks["llm"] = f"error: {exc}"

    ok = checks.get("database") == "ok"
    return {
        "status": "ok" if ok else "degraded",
        "version": settings.app_version,
        "environment": settings.app_env,
        "checks": checks,
    }

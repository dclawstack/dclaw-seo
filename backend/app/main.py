from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.routes import health
from app.api.v1 import (
    ai,
    auth,
    local_seo,
    reports,
    seo,
    settings as settings_router,
    tenancy,
)
from app.core.auth_deps import get_current_user
from app.services.metering import QuotaExceeded

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", app_env=settings.app_env, port=settings.api_port)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    logger.info("shutdown")


app = FastAPI(title="DClaw SEO", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3006"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(QuotaExceeded)
async def _quota_handler(request, exc: QuotaExceeded):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=402, content={"detail": str(exc)})


# Public
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")

# Authenticated (JWT required; LLM calls are metered against the user's org)
_protected = [Depends(get_current_user)]
app.include_router(seo.router, prefix="/api/v1", dependencies=_protected)
app.include_router(ai.router, prefix="/api/v1", dependencies=_protected)
app.include_router(local_seo.router, prefix="/api/v1", dependencies=_protected)
app.include_router(reports.router, prefix="/api/v1", dependencies=_protected)
app.include_router(tenancy.router, prefix="/api/v1")
app.include_router(settings_router.router, prefix="/api/v1", dependencies=_protected)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=True)

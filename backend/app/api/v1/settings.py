from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.settings import LLMSettingsUpdate, LLMSettingsView, LLMTestResult
from app.services.llm import LLMError, Message, llm_service
from app.services.llm_config import get_effective_config, update_config

router = APIRouter(prefix="/settings", tags=["settings"])


def _view(cfg) -> LLMSettingsView:
    key = cfg.openrouter_api_key or ""
    active = next((p for p in cfg.provider_order() if cfg.is_configured(p)), None)
    return LLMSettingsView(
        provider=cfg.provider,
        ollama_url=cfg.ollama_url,
        ollama_model=cfg.ollama_model,
        openrouter_model=cfg.openrouter_model,
        openrouter_api_key_set=bool(key),
        openrouter_api_key_hint=f"…{key[-4:]}" if len(key) >= 4 else None,
        active_provider=active,
    )


@router.get("/llm", response_model=LLMSettingsView)
async def get_llm_settings(db: AsyncSession = Depends(get_db)) -> LLMSettingsView:
    return _view(await get_effective_config(db))


@router.put("/llm", response_model=LLMSettingsView)
async def put_llm_settings(
    body: LLMSettingsUpdate, db: AsyncSession = Depends(get_db)
) -> LLMSettingsView:
    await update_config(db, body.model_dump(exclude_unset=True))
    return _view(await get_effective_config(db))


@router.post("/llm/test", response_model=LLMTestResult)
async def test_llm(db: AsyncSession = Depends(get_db)) -> LLMTestResult:
    cfg = await get_effective_config(db)
    try:
        reply = await llm_service.complete(
            [Message(role="user", content="Reply with the single word: ok")],
            config=cfg,
            temperature=0.0,
        )
    except LLMError as exc:
        active = next((p for p in cfg.provider_order() if cfg.is_configured(p)), None)
        return LLMTestResult(ok=False, provider=active, detail=str(exc))
    active = next((p for p in cfg.provider_order() if cfg.is_configured(p)), None)
    return LLMTestResult(ok=True, provider=active, detail=reply.strip()[:120])

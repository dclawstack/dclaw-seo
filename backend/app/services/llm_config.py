"""Runtime LLM configuration: DB-stored values override env defaults.

Lets the provider/endpoint/token be changed from the app (Settings page)
without a restart. The stored row (id=1) is optional; any blank field falls
back to the environment.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.llm_settings import LLMSettings
from app.services.llm import LLMConfig

_ROW_ID = 1
_EDITABLE = ("provider", "ollama_url", "ollama_model", "openrouter_api_key", "openrouter_model")


async def get_row(db: AsyncSession) -> LLMSettings | None:
    return await db.get(LLMSettings, _ROW_ID)


async def get_effective_config(db: AsyncSession) -> LLMConfig:
    cfg = LLMConfig.from_settings()
    row = await get_row(db)
    if row:
        if row.provider:
            cfg.provider = row.provider
        if row.ollama_url:
            cfg.ollama_url = row.ollama_url
        if row.ollama_model:
            cfg.ollama_model = row.ollama_model
        if row.openrouter_api_key:
            cfg.openrouter_api_key = row.openrouter_api_key
        if row.openrouter_model:
            cfg.openrouter_model = row.openrouter_model
    return cfg


async def update_config(db: AsyncSession, fields: dict) -> LLMSettings:
    row = await get_row(db)
    if row is None:
        row = LLMSettings(id=_ROW_ID)
        db.add(row)
    for key in _EDITABLE:
        if key in fields and fields[key] is not None:
            setattr(row, key, fields[key])
    await db.commit()
    await db.refresh(row)
    return row

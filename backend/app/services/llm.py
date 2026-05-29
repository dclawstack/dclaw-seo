"""Provider-agnostic LLM layer.

One call site (`LLMService.complete`) backed by swappable providers:
- **Ollama** (local) — configured via OLLAMA_URL / OLLAMA_MODEL
- **OpenRouter** (cloud) — configured via OPENROUTER_API_KEY / OPENROUTER_MODEL

Selection is config-driven (`LLM_PROVIDER`): "ollama", "openrouter", or
"auto" (try each configured provider in order, falling back on failure).
Drop your Ollama endpoint or OpenRouter token into `backend/.env`.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMError(RuntimeError):
    """Raised when no configured provider can satisfy a request."""


class LLMNotConfigured(LLMError):
    """Raised when no provider is configured at all."""


@dataclass
class Message:
    role: str  # "system" | "user" | "assistant"
    content: str


class OllamaProvider:
    name = "ollama"

    def __init__(self) -> None:
        self.url = settings.ollama_url.rstrip("/")
        self.model = settings.ollama_model

    async def complete(self, messages: list[Message], *, temperature: float) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            resp = await client.post(f"{self.url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data["message"]["content"]


class OpenRouterProvider:
    name = "openrouter"

    def __init__(self) -> None:
        self.base_url = settings.openrouter_base_url.rstrip("/")
        self.model = settings.openrouter_model
        self.api_key = settings.openrouter_api_key

    async def complete(self, messages: list[Message], *, temperature: float) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]


def _is_configured(provider_name: str) -> bool:
    if provider_name == "ollama":
        return bool(settings.ollama_url and settings.ollama_model)
    if provider_name == "openrouter":
        return bool(settings.openrouter_api_key and settings.openrouter_model)
    return False


def _provider_order() -> list[str]:
    """Resolve the ordered list of providers to attempt, per LLM_PROVIDER."""
    pref = (settings.llm_provider or "auto").lower()
    if pref in ("ollama", "openrouter"):
        return [pref]
    # "auto": local first, then cloud fallback (per REVISED-PRD §4)
    return ["ollama", "openrouter"]


_PROVIDERS = {"ollama": OllamaProvider, "openrouter": OpenRouterProvider}


class LLMService:
    """The single LLM call site for the app."""

    async def complete(
        self,
        messages: list[Message],
        *,
        temperature: float = 0.2,
    ) -> str:
        candidates = [p for p in _provider_order() if _is_configured(p)]
        if not candidates:
            raise LLMNotConfigured(
                "No LLM provider configured. Set OLLAMA_URL/OLLAMA_MODEL or "
                "OPENROUTER_API_KEY/OPENROUTER_MODEL in backend/.env."
            )
        last_error: Exception | None = None
        for name in candidates:
            provider = _PROVIDERS[name]()
            try:
                return await provider.complete(messages, temperature=temperature)
            except Exception as exc:  # try the next configured provider
                last_error = exc
                logger.warning("llm_provider_failed", provider=name, error=str(exc))
        raise LLMError(f"All configured LLM providers failed: {last_error}") from last_error


llm_service = LLMService()

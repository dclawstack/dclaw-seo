"""Provider-agnostic LLM layer.

One call site (`LLMService.complete`) backed by swappable providers:
- **Ollama** (local) — OLLAMA_URL / OLLAMA_MODEL
- **OpenRouter** (cloud) — OPENROUTER_API_KEY / OPENROUTER_MODEL

Configuration is carried in an :class:`LLMConfig`. The effective config is
resolved at request time (DB overrides env — see ``services/llm_config.py``),
so the provider/endpoint/token can be changed from the app without a restart.
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


@dataclass
class LLMConfig:
    provider: str
    ollama_url: str
    ollama_model: str
    openrouter_api_key: str
    openrouter_base_url: str
    openrouter_model: str
    timeout: float = 60.0

    @classmethod
    def from_settings(cls) -> "LLMConfig":
        return cls(
            provider=settings.llm_provider,
            ollama_url=settings.ollama_url,
            ollama_model=settings.ollama_model,
            openrouter_api_key=settings.openrouter_api_key,
            openrouter_base_url=settings.openrouter_base_url,
            openrouter_model=settings.openrouter_model,
            timeout=settings.llm_timeout_seconds,
        )

    def is_configured(self, provider_name: str) -> bool:
        if provider_name == "ollama":
            return bool(self.ollama_url and self.ollama_model)
        if provider_name == "openrouter":
            return bool(self.openrouter_api_key and self.openrouter_model)
        return False

    def provider_order(self) -> list[str]:
        pref = (self.provider or "auto").lower()
        if pref in ("ollama", "openrouter"):
            return [pref]
        return ["ollama", "openrouter"]  # auto: local first, cloud fallback


class OllamaProvider:
    name = "ollama"

    def __init__(self, config: LLMConfig) -> None:
        self.url = config.ollama_url.rstrip("/")
        self.model = config.ollama_model
        self.timeout = config.timeout

    async def complete(self, messages: list[Message], *, temperature: float) -> tuple[str, dict]:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        usage = {
            "model": self.model,
            "prompt_tokens": int(data.get("prompt_eval_count", 0) or 0),
            "completion_tokens": int(data.get("eval_count", 0) or 0),
        }
        return data["message"]["content"], usage


class OpenRouterProvider:
    name = "openrouter"

    def __init__(self, config: LLMConfig) -> None:
        self.base_url = config.openrouter_base_url.rstrip("/")
        self.model = config.openrouter_model
        self.api_key = config.openrouter_api_key
        self.timeout = config.timeout

    async def complete(self, messages: list[Message], *, temperature: float) -> tuple[str, dict]:
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
        u = data.get("usage", {}) or {}
        usage = {
            "model": self.model,
            "prompt_tokens": int(u.get("prompt_tokens", 0) or 0),
            "completion_tokens": int(u.get("completion_tokens", 0) or 0),
        }
        return data["choices"][0]["message"]["content"], usage


_PROVIDERS = {"ollama": OllamaProvider, "openrouter": OpenRouterProvider}


class LLMService:
    """The single LLM call site for the app."""

    async def complete(
        self,
        messages: list[Message],
        *,
        config: LLMConfig | None = None,
        temperature: float = 0.2,
    ) -> str:
        cfg = config or LLMConfig.from_settings()
        candidates = [p for p in cfg.provider_order() if cfg.is_configured(p)]
        if not candidates:
            raise LLMNotConfigured(
                "No LLM provider configured. Set an Ollama endpoint or an OpenRouter "
                "token in Settings (or backend/.env)."
            )

        # Per-org cost cap + usage metering (no-op when unauthenticated/no meter).
        from app.core.context import get_meter
        from app.services import metering

        meter = get_meter()
        if meter is not None:
            await metering.enforce_cap(meter.db, meter.org_id)  # may raise QuotaExceeded

        last_error: Exception | None = None
        for name in candidates:
            provider = _PROVIDERS[name](cfg)
            try:
                text, usage = await provider.complete(messages, temperature=temperature)
            except Exception as exc:  # try the next configured provider
                last_error = exc
                logger.warning("llm_provider_failed", provider=name, error=str(exc))
                continue
            if meter is not None:
                await metering.record(
                    meter.db,
                    meter.org_id,
                    meter.feature,
                    usage.get("model", name),
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0),
                )
            return text
        raise LLMError(f"All configured LLM providers failed: {last_error}") from last_error


llm_service = LLMService()

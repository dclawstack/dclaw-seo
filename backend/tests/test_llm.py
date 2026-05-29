import pytest

from app.core.config import settings
from app.services.llm import (
    LLMError,
    LLMNotConfigured,
    LLMService,
    Message,
    _is_configured,
    _provider_order,
)

_KEYS = [
    "llm_provider",
    "ollama_url",
    "ollama_model",
    "openrouter_api_key",
    "openrouter_model",
]


@pytest.fixture
def reset_settings():
    saved = {k: getattr(settings, k) for k in _KEYS}
    yield
    for k, v in saved.items():
        setattr(settings, k, v)


def test_provider_order_auto_is_local_then_cloud(reset_settings):
    settings.llm_provider = "auto"
    assert _provider_order() == ["ollama", "openrouter"]


def test_provider_order_pinned(reset_settings):
    settings.llm_provider = "openrouter"
    assert _provider_order() == ["openrouter"]


def test_is_configured(reset_settings):
    settings.openrouter_api_key = ""
    assert not _is_configured("openrouter")
    settings.openrouter_api_key = "sk-test"
    settings.openrouter_model = "some/model"
    assert _is_configured("openrouter")
    settings.ollama_url = "http://localhost:11434"
    settings.ollama_model = "llama3.1"
    assert _is_configured("ollama")


@pytest.mark.asyncio
async def test_complete_unconfigured_raises(reset_settings):
    settings.llm_provider = "auto"
    settings.ollama_url = ""
    settings.ollama_model = ""
    settings.openrouter_api_key = ""
    settings.openrouter_model = ""
    with pytest.raises(LLMNotConfigured):
        await LLMService().complete([Message(role="user", content="hi")])


@pytest.mark.asyncio
async def test_complete_unreachable_provider_raises_llmerror(reset_settings):
    # Real connection failure against an unused port exercises the fallback/error path.
    settings.llm_provider = "ollama"
    settings.ollama_url = "http://127.0.0.1:9"
    settings.ollama_model = "llama3.1"
    with pytest.raises(LLMError):
        await LLMService().complete([Message(role="user", content="hi")])

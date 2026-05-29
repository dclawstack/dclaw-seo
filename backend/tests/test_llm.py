import pytest

from app.services.llm import LLMConfig, LLMError, LLMNotConfigured, LLMService, Message


def cfg(**kw):
    base = dict(
        provider="auto",
        ollama_url="",
        ollama_model="",
        openrouter_api_key="",
        openrouter_base_url="https://openrouter.ai/api/v1",
        openrouter_model="",
        timeout=5.0,
    )
    base.update(kw)
    return LLMConfig(**base)


def test_provider_order_auto_is_local_then_cloud():
    assert cfg(provider="auto").provider_order() == ["ollama", "openrouter"]


def test_provider_order_pinned():
    assert cfg(provider="openrouter").provider_order() == ["openrouter"]


def test_is_configured():
    assert not cfg().is_configured("openrouter")
    assert cfg(openrouter_api_key="sk", openrouter_model="m").is_configured("openrouter")
    assert cfg(ollama_url="http://localhost:11434", ollama_model="llama3.2:3b").is_configured(
        "ollama"
    )


@pytest.mark.asyncio
async def test_complete_unconfigured_raises():
    with pytest.raises(LLMNotConfigured):
        await LLMService().complete([Message(role="user", content="hi")], config=cfg())


@pytest.mark.asyncio
async def test_complete_unreachable_provider_raises_llmerror():
    c = cfg(provider="ollama", ollama_url="http://127.0.0.1:9", ollama_model="llama3.1")
    with pytest.raises(LLMError):
        await LLMService().complete([Message(role="user", content="hi")], config=c)

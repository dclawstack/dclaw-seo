import pytest


@pytest.mark.asyncio
async def test_get_llm_settings_defaults(client):
    resp = await client.get("/api/v1/settings/llm")
    assert resp.status_code == 200
    body = resp.json()
    assert "provider" in body
    assert body["openrouter_api_key_set"] is False


@pytest.mark.asyncio
async def test_put_llm_settings_persists_and_masks(client):
    resp = await client.put(
        "/api/v1/settings/llm",
        json={
            "provider": "ollama",
            "ollama_url": "http://host.docker.internal:11434",
            "ollama_model": "llama3.2:3b",
            "openrouter_api_key": "sk-or-secret-1234",
            "openrouter_model": "anthropic/claude-3.5-sonnet",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider"] == "ollama"
    assert body["ollama_url"] == "http://host.docker.internal:11434"
    assert body["ollama_model"] == "llama3.2:3b"
    # key is stored but never returned in full
    assert body["openrouter_api_key_set"] is True
    assert body["openrouter_api_key_hint"] == "…1234"
    assert "secret" not in str(body)
    # active provider resolves to ollama (configured + pinned)
    assert body["active_provider"] == "ollama"

    # persisted across requests
    again = (await client.get("/api/v1/settings/llm")).json()
    assert again["ollama_model"] == "llama3.2:3b"
    assert again["openrouter_api_key_set"] is True

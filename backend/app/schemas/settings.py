from typing import Optional

from pydantic import BaseModel, Field


class LLMSettingsUpdate(BaseModel):
    provider: Optional[str] = Field(None, description="auto | ollama | openrouter")
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_model: Optional[str] = None


class LLMSettingsView(BaseModel):
    provider: str
    ollama_url: str
    ollama_model: str
    openrouter_model: str
    openrouter_api_key_set: bool
    openrouter_api_key_hint: Optional[str] = None  # last 4 chars, if set
    active_provider: Optional[str] = None  # first configured provider in the resolved order


class LLMTestResult(BaseModel):
    ok: bool
    provider: Optional[str] = None
    detail: str

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8095
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_seo"

    # --- LLM provider (configure one or both; see services/llm.py) ---
    # Preference order: "auto" tries ollama then openrouter; or pin "ollama"/"openrouter".
    llm_provider: str = "auto"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct"
    llm_timeout_seconds: float = 60.0

    # --- PageSpeed Insights (Core Web Vitals); optional free key for quota ---
    pagespeed_api_key: str = ""

    # --- Google Business Profile (Local SEO); optional, enables live GBP sync ---
    gbp_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

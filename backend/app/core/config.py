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

    # --- Auth (self-contained JWT) ---
    secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # --- LLM cost metering (per-org ledger + cost cap) ---
    # Default rate for cloud tokens; local Ollama is treated as $0 but still metered.
    llm_cost_per_1k_tokens_usd: float = 0.0

    # --- Billing (Stripe); optional — local invoice math works without it ---
    stripe_api_key: str = ""
    stripe_base_url: str = "https://api.stripe.com/v1"

    # --- SMTP (scheduled white-label report delivery); optional ---
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "reports@dclaw-seo.local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

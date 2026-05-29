from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8095
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_seo"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

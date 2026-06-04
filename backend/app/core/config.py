from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Padrão de desenvolvimento: SQLite local (zero configuração).
    # Em produção/Docker, defina DATABASE_URL para o Postgres no .env.
    database_url: str = "sqlite:///./imsfay_dev.db"
    redis_url: str = "redis://localhost:6379/0"

    brapi_token: str = ""

    # Liga os cronjobs (APScheduler). Mantenha False em dev com --reload.
    enable_scheduler: bool = False

    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

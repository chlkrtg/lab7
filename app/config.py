from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FastAPI Async Lab"
    redis_url: str = "redis://localhost:6379/0"
    task_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
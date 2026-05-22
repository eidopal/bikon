from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemini-3.5-flash"

    DATABASE_URL: str = "sqlite+aiosqlite:///./bikon.db"

    REDIS_URL: str = "redis://localhost:6379/0"

    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    STORAGE_PATH: str = "./static/uploads"
    BASE_URL: str = "http://localhost:8000"

    SECRET_KEY: str = "dev_secret_key"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()

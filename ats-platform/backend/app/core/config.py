"""
app/core/config.py
------------------
Centralised application settings loaded from environment variables.
Pydantic Settings validates and parses every value at startup.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ---- Application ----
    APP_NAME: str = "ATS Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ---- Database ----
    DATABASE_URL: str = "sqlite:///./ats.db"

    # ---- Security ----
    SECRET_KEY: str = "change-this-secret-key-in-production"

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ats-platform-2htwduh19-prasadbole-12s-projects.vercel.app",
    ]

    # ---- File Uploads ----
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "docx"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
import os
from functools import lru_cache
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a local .env if present
load_dotenv()


class Settings(BaseSettings):
    environment: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./aegis_local.db")
    jwt_secret_key: str = os.getenv("SECRET_KEY", "change-me-in-prod")
    jwt_algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

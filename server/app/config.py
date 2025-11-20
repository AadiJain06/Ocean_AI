import os
from functools import lru_cache


class Settings:
    app_name: str = "Ocean AI Author"
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite:///./ocean_ai.db"
    )
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()


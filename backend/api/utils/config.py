import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    APP_NAME: str = "Period Tracker API"
    FIRST_USER: str  # = "admin"
    FIRST_USER_PASS: str  # = "adminpass"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


settings = Settings()  # type: ignore

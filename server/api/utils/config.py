from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str = "beans@example.com"
    items_per_user: int = 50
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    secret_key: str = ""
    algorithm: str = "HS256"


settings = Settings()

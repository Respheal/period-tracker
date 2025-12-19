import secrets
import warnings
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    APP_NAME: str = "Period Tracker API"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["local", "test", "production"]
    SMOOTHING_FACTOR: int = 3  # Higher values reduce data noise but are less responsive
    FIRST_USER: str  # = "admin"
    FIRST_USER_PASS: str  # = "adminpass"
    DATABASE: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Deprecated, use RSA keys instead
    PRIVATE_KEY_PATH: str | None = None  # Path to RSA private key for RS256
    PUBLIC_KEY_PATH: str | None = None  # Path to RSA public key for RS256
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    # Cached keys to avoid reading from disk on every request
    _private_key_bytes: bytes | None = None
    _public_key_bytes: bytes | None = None

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = f'The value of {var_name} is "changethis"'
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            elif self.ENVIRONMENT == "test":
                print(f"WARNING: {message}")
            else:
                # In production, raise an error
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        # Only check SECRET_KEY if using HS256 (symmetric algorithm)
        if self.ALGORITHM != "RS256":
            self._check_default_secret("SECRET_KEY", self.SECRET_KEY)

        self._check_default_secret("FIRST_SUPERUSER_PASSWORD", self.FIRST_USER_PASS)

        # Validate RSA configuration for RS256
        if self.ALGORITHM == "RS256":
            if not self.PRIVATE_KEY_PATH or not self.PUBLIC_KEY_PATH:
                raise ValueError(
                    "PRIVATE_KEY_PATH and PUBLIC_KEY_PATH must "
                    "be set when using RS256 algorithm."
                )
            # Load keys on initialization
            self._load_rsa_keys()

        return self

    def _load_rsa_keys(self) -> None:
        """Load RSA keys from files and cache them in memory."""
        if self.PRIVATE_KEY_PATH:
            private_key_file = Path(self.PRIVATE_KEY_PATH)
            if not private_key_file.exists():
                raise FileNotFoundError(
                    f"Private key file not found: {self.PRIVATE_KEY_PATH}"
                )
            self._private_key_bytes = private_key_file.read_bytes()

        if self.PUBLIC_KEY_PATH:
            public_key_file = Path(self.PUBLIC_KEY_PATH)
            if not public_key_file.exists():
                raise FileNotFoundError(
                    f"Public key file not found: {self.PUBLIC_KEY_PATH}"
                )
            self._public_key_bytes = public_key_file.read_bytes()

    def get_private_key(self) -> bytes:
        """Get the private key for signing tokens (RS256)."""
        if self.ALGORITHM == "RS256":
            if self._private_key_bytes is None:
                raise ValueError("Private key not loaded for RS256 algorithm")
            return self._private_key_bytes
        # Fallback to SECRET_KEY for HS256 (backward compatibility)
        return self.SECRET_KEY.encode()

    def get_public_key(self) -> bytes:
        """Get the public key for verifying tokens (RS256)."""
        if self.ALGORITHM == "RS256":
            if self._public_key_bytes is None:
                raise ValueError("Public key not loaded for RS256 algorithm")
            return self._public_key_bytes
        # Fallback to SECRET_KEY for HS256 (backward compatibility)
        return self.SECRET_KEY.encode()


settings = Settings()  # type: ignore

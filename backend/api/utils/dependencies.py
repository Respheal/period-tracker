from collections.abc import Generator
from functools import lru_cache

from sqlmodel import Session

from api.db.session import engine
from api.utils.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session

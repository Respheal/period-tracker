from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Query
from sqlmodel import Session

from api.db.session import engine
from api.utils.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


class CommonUserParams:
    """Common parameters for use in User search endpoints."""

    def __init__(
        self,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100,
    ):
        self.offset = offset
        self.limit = limit


class CommonEventParams:
    """Common parameters for use in Event search endpoints."""

    def __init__(
        self,
        start_date: Annotated[
            str | None,
            Query(description="Start date filter", pattern=r"^\d{4}-\d{2}-\d{2}$"),
        ] = None,
        end_date: Annotated[
            str | None,
            Query(description="End date filter", pattern=r"^\d{4}-\d{2}-\d{2}$"),
        ] = None,
        offset: int = 0,
        limit: Annotated[int, Query(le=365)] = 100,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.offset = offset
        self.limit = limit

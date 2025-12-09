from collections.abc import Generator

from sqlmodel import Session

from api.db.session import engine


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session

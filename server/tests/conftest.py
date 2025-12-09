from collections.abc import Generator

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlmodel import Session

from alembic import command
from api.db.session import engine
from api.main import app


@pytest.fixture
def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


# Apply migrations at beginning and end of testing session
@pytest.fixture(autouse=True)
def apply_migrations() -> Generator:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", "sqlite:///test.db")
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")

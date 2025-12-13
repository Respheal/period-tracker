from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from alembic import command
from alembic.config import Config
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
    command.upgrade(config, "head")
    yield
    command.downgrade(config, "base")


@pytest.fixture(scope="module")
def admin_token_headers(client: TestClient) -> dict[str, str]:
    return {}


@pytest.fixture(scope="module")
def user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return {}

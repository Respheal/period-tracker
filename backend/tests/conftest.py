from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from alembic import command
from alembic.config import Config
from api.db.session import engine
from api.main import app
from api.utils.config import Settings

# function: the default scope, the fixture is destroyed at the end of the test.
# class: the fixture is destroyed during teardown of the last test in the class.
# module: the fixture is destroyed during teardown of the last test in the module.
# package: the fixture is destroyed during teardown of the last test in the package.
# session: the fixture is destroyed at the end of the test session.


@pytest.fixture(scope="module")
def settings() -> Settings:
    return Settings()


@pytest.fixture
def session() -> Generator[Session]:
    with Session(engine) as db_session:
        yield db_session


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


# Apply migrations at beginning and end of testing session
@pytest.fixture(autouse=True, scope="module")
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

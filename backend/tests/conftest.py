from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db.session import engine
from api.initial_data import init
from api.main import app
from api.utils.config import Settings
from tests.utils import get_admin_headers, get_user_headers

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
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise
        finally:
            db_session.close()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


# Apply migrations at beginning and end of testing session
@pytest.fixture(autouse=True, scope="module")
def apply_migrations() -> Generator:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    init()
    yield
    command.downgrade(config, "base")


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    return get_admin_headers(client)


@pytest.fixture
def user_headers(client: TestClient, session: Session) -> dict[str, str]:
    return get_user_headers(client=client, username="testjim", db=session)

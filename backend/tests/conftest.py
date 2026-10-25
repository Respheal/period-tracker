from collections.abc import Generator
from threading import Thread

import pytest
from alembic import command
from alembic.config import Config
from fakeredis import TcpFakeServer
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from api.db.session import engine
from api.initial_data import init
from api.main import app
from api.utils.config import Settings
from tests.utils.auth import get_admin_headers, get_user_headers

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


@pytest.fixture(autouse=True, scope="session")
def redis_server() -> Generator:
    server = TcpFakeServer(
        (Settings().REDIS_HOST, Settings().REDIS_PORT), server_type="redis"
    )
    # Added to stop the pytest process from hanging due to the server thread
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()


# Apply migrations at beginning and end of the test session
@pytest.fixture(autouse=True, scope="session")
def setup() -> Generator:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    init()
    yield
    command.downgrade(config, "base")


# Clear the database before each test function
@pytest.fixture(autouse=True, scope="function")
def clear_db() -> Generator:
    with engine.begin() as connection:
        # reversed to respect FK-constraints
        for table in reversed(models.metadata.sorted_tables):
            connection.execute(table.delete())
    init()
    yield


@pytest.fixture
def admin_headers(client: TestClient) -> dict[str, str]:
    return get_admin_headers(client)


@pytest.fixture
def user_headers(client: TestClient, session: Session) -> dict[str, str]:
    return get_user_headers(client=client, username="jim", db=session)

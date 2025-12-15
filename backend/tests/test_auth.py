from threading import Thread

import pytest
from fakeredis import TcpFakeServer
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.utils import auth
from api.utils.config import Settings
from api.utils.redis_client import get_redis_client
from tests.utils import random_lower_string
from tests.utils.user import create_random_user


def test_login(client: TestClient, session: Session) -> None:
    password = random_lower_string()
    user = create_random_user(session, password=password)

    # Test with incorrect password first
    r = client.post(
        "/auth/",
        data={
            "username": user.username,
            "password": "wrongpassword",
        },
    )
    assert r.status_code == 401
    assert "refresh_token" not in r.cookies

    # Now test with correct password
    r = client.post(
        "/auth/",
        data={
            "username": user.username,
            "password": password,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert r.cookies["refresh_token"]

    # try using the refresh token as the access token
    r = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {r.cookies['refresh_token']}"},
    )
    assert r.status_code == 401


# consider making this a pytest fixture
def test_refresh_tokens(client: TestClient, session: Session, settings: Settings) -> None:
    # Set up a fake Redis TCP server on the configured Redis host and port
    server_address = (settings.REDIS_HOST, settings.REDIS_PORT)
    fake_server = TcpFakeServer(server_address, server_type="redis")
    server_thread = Thread(target=fake_server.serve_forever, daemon=True)
    server_thread.start()

    try:
        password = random_lower_string()
        user = create_random_user(session, password=password)
        r = client.post(
            "/auth/",
            data={"username": user.username, "password": password},
        )
        assert r.status_code == 200

        refresh_token = r.cookies["refresh_token"]
        access_token = r.json()["access_token"]
        old_refresh_jti = auth.validate_token(
            token=refresh_token,
            token_type="refresh",
            settings=settings,
        ).jti
        old_access_jti = auth.validate_token(
            token=access_token,
            token_type="access",
            settings=settings,
        ).jti

        # Ensure the old refresh token is in the client cookies, then attempt the refresh
        client.cookies.set("refresh_token", refresh_token)
        r = client.post("/auth/refresh")
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert r.cookies["refresh_token"]
        new_refresh_token = r.cookies["refresh_token"]
        new_refresh_jti = auth.validate_token(
            token=new_refresh_token,
            token_type="refresh",
            settings=settings,
        ).jti
        new_access_jti = auth.validate_token(
            token=data["access_token"],
            token_type="access",
            settings=settings,
        ).jti

        assert new_access_jti != old_access_jti
        assert new_refresh_jti != old_refresh_jti

        # Verify that the old token is blacklisted in redis
        assert get_redis_client().get(f"{old_refresh_jti}")

        # Test with missing refresh token
        client.cookies.delete("refresh_token")
        r = client.post("/auth/refresh")
        assert r.status_code == 401
    finally:
        # Shut down the fake server
        fake_server.shutdown()


def test_refresh_tokens_disabled_user(
    client: TestClient, session: Session, settings: Settings
) -> None:
    password = random_lower_string()
    user = create_random_user(session, password=password)

    r = client.post(
        "/auth/",
        data={"username": user.username, "password": password},
    )
    assert r.status_code == 200
    refresh_token = r.cookies["refresh_token"]

    # Disable the user
    user.is_disabled = True
    session.add(user)
    session.commit()

    # Try to refresh tokens
    client.cookies.set("refresh_token", refresh_token)
    r = client.post("/auth/refresh")
    assert r.status_code == 401

    session.delete(user)
    session.commit()

    # Try to refresh tokens
    client.cookies.set("refresh_token", refresh_token)
    r = client.post("/auth/refresh")
    assert r.status_code == 401


def test_refresh_with_access_token(
    client: TestClient, session: Session, settings: Settings
) -> None:
    password = random_lower_string()
    user = create_random_user(session, password=password)

    r = client.post(
        "/auth/",
        data={"username": user.username, "password": password},
    )
    assert r.status_code == 200
    access_token = r.json()["access_token"]

    # Try to refresh tokens using access token instead of refresh token
    client.cookies.set("refresh_token", access_token)
    r = client.post("/auth/refresh")
    assert r.status_code == 401


def test_incorrect_token_type(session: Session) -> None:
    settings = Settings()
    user = create_random_user(session)
    with pytest.raises(ValueError):
        auth.create_token(
            user=user,
            token_type="nonexistent",  # nosec B106
            settings=settings,
        )

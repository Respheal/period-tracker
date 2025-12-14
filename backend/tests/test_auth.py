from fastapi.testclient import TestClient
from sqlmodel import Session

from api.utils import auth
from api.utils.config import Settings
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


def test_refresh_tokens(client: TestClient, session: Session, settings: Settings) -> None:
    password = random_lower_string()
    user = create_random_user(session, password=password)
    r = client.post(
        "/auth/",
        data={"username": user.username, "password": password},
    )
    assert r.status_code == 200
    access_token = r.json()["access_token"]
    refresh_token = r.cookies["refresh_token"]
    old_refresh_jti = auth.validate_token(
        token=refresh_token, token_type="refresh", settings=settings
    ).jti
    old_access_jti = auth.validate_token(
        token=access_token, token_type="access", settings=settings
    ).jti

    # Make sure the old refresh token is in the client cookies
    # before attempting the refresh
    client.cookies.set("refresh_token", refresh_token)
    r = client.post("/auth/refresh")
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert r.cookies["refresh_token"]
    new_refresh_token = r.cookies["refresh_token"]
    new_refresh_jti = auth.validate_token(
        token=new_refresh_token, token_type="refresh", settings=settings
    ).jti
    new_access_jti = auth.validate_token(
        token=data["access_token"], token_type="access", settings=settings
    ).jti

    assert new_access_jti != old_access_jti
    assert new_refresh_jti != old_refresh_jti

    # TODO: Figure how to test that the old refresh token is revoked
    # TODO: Test that disabled users cannot refresh tokens
    # TODO: Test that deleted users cannot refresh tokens

    # Test with missing refresh token
    client.cookies.delete("refresh_token")
    r = client.post("/auth/refresh")
    assert r.status_code == 401

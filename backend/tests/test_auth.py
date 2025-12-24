import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.utils import auth
from api.utils.config import Settings
from api.utils.redis_client import get_redis_client
from tests.utils import random_lower_string
from tests.utils.auth import login_user
from tests.utils.user import create_random_user


class TestLogin:
    def test_login_with_correct_password(
        self, client: TestClient, session: Session
    ) -> None:
        password = random_lower_string()
        user = create_random_user(session, password=password)
        response = client.post(
            "/auth/",
            data={
                "username": user.username,
                "password": password,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert response.cookies["refresh_token"]

    def test_login_with_incorrect_password(
        self, client: TestClient, session: Session
    ) -> None:
        password = random_lower_string()
        user = create_random_user(session, password=password)

        response = client.post(
            "/auth/",
            data={
                "username": user.username,
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "refresh_token" not in response.cookies

    def test_refresh_token_cannot_be_used_as_access_token(
        self, client: TestClient, session: Session
    ) -> None:
        login = login_user(client, session)
        assert login["response"].status_code == 200, login["response"]
        refresh_token = login["response"].cookies["refresh_token"]
        # Try using the refresh token as the access token
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert response.status_code == 401


class TestTokenRefresh:
    def test_refresh_tokens(
        self, client: TestClient, session: Session, settings: Settings
    ) -> None:
        login = login_user(client, session)
        assert login["response"].status_code == 200
        refresh_token = login["response"].cookies["refresh_token"]
        access_token = login["response"].json()["access_token"]

        # Get JTI from old tokens
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

        # Attempt the refresh
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 200

        data = response.json()
        assert "access_token" in data
        assert response.cookies["refresh_token"]

        # Get JTI from new tokens
        new_refresh_token = response.cookies["refresh_token"]
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

        # Verify new tokens have different JTIs
        assert new_access_jti != old_access_jti
        assert new_refresh_jti != old_refresh_jti

        # Verify that the old token is blacklisted in redis
        assert get_redis_client().get(f"{old_refresh_jti}")

    def test_refresh_with_missing_token(self, client: TestClient) -> None:
        client.cookies.delete("refresh_token")
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_with_access_token(
        self, client: TestClient, session: Session
    ) -> None:
        login = login_user(client, session)
        assert login["response"].status_code == 200
        access_token = login["response"].json()["access_token"]

        # Try to refresh tokens using access token instead of refresh token
        client.cookies.set("refresh_token", access_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401


class TestTokenRefreshEdgeCases:
    def test_refresh_tokens_disabled_user(
        self, client: TestClient, session: Session
    ) -> None:
        login = login_user(client, session)
        assert login["response"].status_code == 200
        refresh_token = login["response"].cookies["refresh_token"]
        user = login["user"]

        # Disable the user
        user.is_disabled = True
        session.add(user)
        session.commit()

        # Try to refresh tokens with disabled user
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_tokens_deleted_user(
        self, client: TestClient, session: Session
    ) -> None:
        login = login_user(client, session)
        assert login["response"].status_code == 200
        refresh_token = login["response"].cookies["refresh_token"]
        user = login["user"]

        # Delete the user
        session.delete(user)
        session.commit()

        # Try to refresh tokens with deleted user
        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401


class TestTokenCreation:
    def test_incorrect_token_type(self, session: Session) -> None:
        settings = Settings()
        user = create_random_user(session)

        with pytest.raises(ValueError):
            auth.create_token(
                user=user,
                token_type="nonexistent",  # nosec B106
                settings=settings,
            )

    def test_invalid_token(self, client: TestClient) -> None:
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert response.status_code == 401

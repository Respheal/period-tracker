from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from tests.utils import is_valid_uuid
from tests.utils.user import create_random_user


def test_create_user(client: TestClient) -> None:
    response = client.post(
        "/users/", json={"username": "Alice", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "Alice"
    assert data["display_name"] is None
    assert data["is_disabled"] is False
    assert data["is_admin"] is False
    assert is_valid_uuid(data["user_id"])

    # Test for a duplicate username
    response = client.post(
        "/users/", json={"username": "Alice", "password": "password123"}
    )
    assert response.status_code == 409


def test_get_users(
    session: Session,
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
) -> None:
    # Assure we have at least one user in the list
    create_random_user(session)
    # Should succeed for admin
    response = client.get("/users/", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    # Each user should have expected keys (UserSafe)
    if users:
        user = users[0]
        assert "user_id" in user
        assert "username" in user
        assert "display_name" in user
        assert "is_disabled" in user
        assert "is_admin" in user
        assert "hashed_password" not in user  # sensitive info should not be present
        assert "average_cycle_length" not in user
        assert "average_period_length" not in user

    # Should fail for non-admin
    response = client.get("/users/", headers=user_headers)
    assert response.status_code == 403

    # Should fail for unauthenticated
    response = client.get("/users/")
    assert response.status_code == 401


def test_read_me(client: TestClient, user_headers: dict[str, str]) -> None:
    r = client.get("/users/me", headers=user_headers)
    current_user = r.json()
    assert current_user
    assert "username" in current_user
    assert current_user["username"] == "jim"
    assert current_user["is_admin"] is False
    assert current_user["is_disabled"] is False
    assert is_valid_uuid(current_user["user_id"])


def test_update_me(
    client: TestClient, user_headers: dict[str, str], session: Session
) -> None:
    # Update display_name and check response
    update_data = {"display_name": "Jimbo"}
    response = client.patch("/users/me/", json=update_data, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Jimbo"
    assert is_valid_uuid(data["user_id"])


def test_delete_me(
    client: TestClient, user_headers: dict[str, str], session: Session
) -> None:
    # Delete current user
    response = client.delete("/users/me/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["resource_type"] == "user"
    assert is_valid_uuid(data["resource_id"])

    # Subsequent get_me should fail
    response = client.get("/users/me/", headers=user_headers)
    assert response.status_code == 401

    # Verify user is actually deleted from DB
    user_id = data["resource_id"]
    assert session.get(models.User, user_id) is None

    # Unauthenticated test
    response = client.delete("/users/me/")
    assert response.status_code == 401

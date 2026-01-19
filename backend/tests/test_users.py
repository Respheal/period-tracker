from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from api.db.crud.user import add_partner, is_partner
from tests.utils import is_valid_uuid
from tests.utils.auth import get_user_headers
from tests.utils.events import (
    create_period_events,
    create_symptom_events,
    create_temperature_readings,
)
from tests.utils.user import create_random_user


class TestUserCreation:
    def test_create_user(self, client: TestClient) -> None:
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

    def test_create_duplicate_username(self, client: TestClient) -> None:
        # Create first user
        client.post("/users/", json={"username": "Alice", "password": "password123"})

        # Attempt to create duplicate
        response = client.post(
            "/users/", json={"username": "Alice", "password": "password123"}
        )
        assert response.status_code == 409


class TestUserRetrieval:
    def test_get_users_as_admin(
        self,
        session: Session,
        client: TestClient,
        admin_headers: dict[str, str],
    ) -> None:
        # Ensure we have at least one user in the list
        create_random_user(session)

        response = client.get("/users/", headers=admin_headers)
        assert response.status_code == 200
        response_json = response.json()
        assert "count" in response_json
        assert response_json["count"] >= 1
        assert "data" in response_json
        assert "users" in response_json["data"]

        # Verify user structure (UserSafe)
        if response_json["data"]["users"]:
            user = response_json["data"]["users"][0]
            assert "user_id" in user
            assert "username" in user
            assert "display_name" in user
            assert "is_disabled" in user
            assert "is_admin" in user
            # Sensitive info should not be present
            assert "hashed_password" not in user
            assert "average_cycle_length" not in user
            assert "average_period_length" not in user

    def test_get_users_as_non_admin(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/users/", headers=user_headers)
        assert response.status_code == 403

    def test_get_users_unauthenticated(self, client: TestClient) -> None:
        response = client.get("/users/")
        assert response.status_code == 401


class TestCurrentUser:
    def test_read_me(self, client: TestClient, user_headers: dict[str, str]) -> None:
        response = client.get("/users/me", headers=user_headers)
        assert response.status_code == 200

        current_user = response.json()
        assert current_user
        assert "username" in current_user
        assert current_user["username"] == "jim"
        assert current_user["is_admin"] is False
        assert current_user["is_disabled"] is False
        assert is_valid_uuid(current_user["user_id"])

    def test_update_me(self, client: TestClient, user_headers: dict[str, str]) -> None:
        # Update display_name
        update_data = {"display_name": "Jimbo"}
        response = client.patch("/users/me/", json=update_data, headers=user_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["display_name"] == "Jimbo"
        assert is_valid_uuid(data["user_id"])

    def test_delete_me(
        self,
        client: TestClient,
        user_headers: dict[str, str],
        session: Session,
    ) -> None:
        # Delete current user
        response = client.delete("/users/me/", headers=user_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["resource_type"] == "user"
        assert is_valid_uuid(data["resource_id"])

        user_id = data["resource_id"]

        # Subsequent get_me should fail
        response = client.get("/users/me/", headers=user_headers)
        assert response.status_code == 401

        # Verify user is actually deleted from DB
        assert session.get(models.User, user_id) is None

    def test_delete_me_unauthenticated(self, client: TestClient) -> None:
        response = client.delete("/users/me/")
        assert response.status_code == 401


class TestGetMyEvents:
    def test_get_my_events(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)
        today = datetime.now(UTC)
        yesterday = today - timedelta(days=1)
        create_period_events(session, user, [(yesterday, today)])
        create_symptom_events(session, user, [{"symptoms": ["cramps"]}])
        create_temperature_readings(session, user, [36.5])

        response = client.get("/users/me/events/", headers=user_headers)
        assert response.status_code == 200
        response_json = response.json()
        assert "count" in response_json
        assert response_json["count"] == 3
        assert "data" in response_json
        assert "periods" in response_json["data"]
        assert "symptoms" in response_json["data"]
        assert "temperatures" in response_json["data"]
        assert (
            yesterday.date().isoformat()
            in response_json["data"]["periods"][0]["start_date"]
        )
        assert today.date().isoformat() in response_json["data"]["periods"][0]["end_date"]
        assert response_json["data"]["symptoms"][0]["symptoms"] == ["cramps"]
        assert response_json["data"]["temperatures"][0]["temperature"] == 36.5

    def test_get_my_events_no_events(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/users/me/events/", headers=user_headers)
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["count"] == 0
        assert "periods" in response_json["data"]
        assert "symptoms" in response_json["data"]
        assert "temperatures" in response_json["data"]
        assert response_json["data"]["periods"] == []
        assert response_json["data"]["symptoms"] == []
        assert response_json["data"]["temperatures"] == []

    def test_get_my_events_unauthenticated(self, client: TestClient) -> None:
        response = client.get("/users/me/events/")
        assert response.status_code == 401


class TestIsPartner:
    def test_is_partner(self, client: TestClient, session: Session) -> None:
        # Create two users and add one as partner to the other
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        add_partner(session=session, user=user1, partner=user2)
        session.refresh(user1)
        assert is_partner(session, user1, user2.user_id) is True

    def test_is_not_partner(self, client: TestClient, session: Session) -> None:
        # Create two users without partnership
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        assert is_partner(session, user1, user2.user_id) is False

    def test_partner_not_found(self, client: TestClient, session: Session) -> None:
        # Create a user
        user1 = create_random_user(session)
        # Check partnership with non-existent user
        assert is_partner(session, user1, "non-existent-id") is False


class TestGetMyPartners:
    def test_get_my_partners(self, client: TestClient, session: Session) -> None:
        # Create two users and add one as partner to the other
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        user1_headers = get_user_headers(client, session, user1.username)
        # Add partner
        client.post(f"/users/me/partners/{user2.user_id}/", headers=user1_headers)
        # Get partners
        response = client.get("/users/me/partners/", headers=user1_headers)
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] == 1
        assert "data" in data
        assert "partners" in data["data"]
        assert isinstance(data["data"]["partners"], list)
        assert any(p["user_id"] == user2.user_id for p in data["data"]["partners"])

    def test_no_partners(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)
        response = client.get("/users/me/partners/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert "partners" in data["data"]
        assert data["data"]["partners"] == []

    def test_get_my_partners_unauthenticated(self, client: TestClient) -> None:
        response = client.get("/users/me/partners/")
        assert response.status_code == 401


class TestAddPartner:
    def test_add_partner_success(self, client: TestClient, session: Session) -> None:
        # Create two users
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        user1_headers = get_user_headers(client, session, user1.username)

        response = client.post(
            f"/users/me/partners/{user2.user_id}/",
            headers=user1_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["user_id"] == user1.user_id
        assert any(p["user_id"] == user2.user_id for p in data.get("partners", []))

    def test_add_partner_not_found(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)

        response = client.post(
            "/users/me/partners/fake-partner-id/",
            headers=user_headers,
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Partner not found."

    def test_add_partner_unauthenticated(self, client: TestClient) -> None:
        response = client.post("/users/me/partners/fake-partner-id/")
        assert response.status_code == 401


class TestRemovePartner:
    def test_remove_partner(self, client: TestClient, session: Session) -> None:
        # Create two users and add one as partner to the other
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        user1_headers = get_user_headers(client, session, user1.username)
        # Add partner
        client.post(f"/users/me/partners/{user2.user_id}/", headers=user1_headers)
        # Remove partner
        response = client.delete(
            f"/users/me/partners/{user2.user_id}/", headers=user1_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["resource_type"] == "partner"
        assert data["resource_id"] == user2.user_id
        # Verify partner is removed
        response = client.get("/users/me/partners/", headers=user1_headers)
        assert response.status_code == 200
        partners = response.json()["data"]["partners"]
        assert all(p["user_id"] != user2.user_id for p in partners)

    def test_remove_partner_not_found(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)
        response = client.delete(
            "/users/me/partners/fake-partner-id/", headers=user_headers
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Partner not found."

    def test_remove_partner_unauthenticated(self, client: TestClient) -> None:
        response = client.delete("/users/me/partners/fake-partner-id/")
        assert response.status_code == 401

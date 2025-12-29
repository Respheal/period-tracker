from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from tests.utils.auth import get_user_headers
from tests.utils.user import create_random_user


class TestPeriodCreation:
    def test_create_period_event(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2025-01-01", "end_date": "2025-01-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "start_date" in data
        assert "end_date" in data
        assert data["start_date"] == "2025-01-01T00:00:00"
        assert data["end_date"] == "2025-01-05T23:59:59.999999"
        assert data["duration"] == 4


class TestPeriodRetrieval:
    def test_get_my_periods(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create some period events
        for i in range(3):
            start_date = datetime.now(UTC) - timedelta(days=30 * (i + 1))
            end_date = start_date + timedelta(days=5)
            client.post(
                "/period/",
                headers=user_headers,
                json={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            )

        response = client.get("/period/me/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] >= 3
        assert isinstance(data["events"], list)

    def test_get_single_period(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a period
        create_response = client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2025-01-01", "end_date": "2025-01-05"},
        )
        assert create_response.status_code == 200
        period_id = create_response.json()["pid"]

        # Retrieve the specific period
        response = client.get(f"/period/me/{period_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["pid"] == period_id

    def test_get_single_period_not_found(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/period/me/99999", headers=user_headers)
        assert response.status_code == 404


class TestPeriodUpdate:
    def test_update_period(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a period
        create_response = client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2025-03-01", "end_date": "2025-03-05"},
        )
        assert create_response.status_code == 200
        period_id = create_response.json()["pid"]

        # Update the period
        response = client.patch(
            f"/period/me/{period_id}",
            headers=user_headers,
            json={"start_date": "2025-01-01", "end_date": "2025-01-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "2025-01-01" in data["start_date"]
        assert "2025-01-05" in data["end_date"]

        # Test that we can remove an end date
        response = client.patch(
            f"/period/me/{period_id}",
            headers=user_headers,
            json={"end_date": None},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["end_date"] is None

    def test_update_period_not_found(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.patch(
            "/period/me/99999",
            headers=user_headers,
            json={"end_date": "2025-01-06"},
        )
        assert response.status_code == 404


class TestPeriodDeletion:
    def test_delete_period(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a period
        create_response = client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2025-01-01", "end_date": "2025-01-05"},
        )
        assert create_response.status_code == 200
        period_id = create_response.json()["pid"]

        # Delete the period
        response = client.delete(f"/period/me/{period_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["resource_type"] == "period"
        assert data["resource_id"] == str(period_id)

        # Verify it's actually deleted
        get_response = client.get(f"/period/me/{period_id}", headers=user_headers)
        assert get_response.status_code == 404

    def test_delete_period_not_found(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.delete("/period/me/99999", headers=user_headers)
        assert response.status_code == 404


class TestPeriodAdminAccess:
    def test_get_all_periods_as_admin(
        self,
        session: Session,
        client: TestClient,
        admin_headers: dict[str, str],
    ) -> None:
        # Create periods for different users
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        user1_headers = get_user_headers(client, session, user1.username)
        user2_headers = get_user_headers(client, session, user2.username)

        client.post(
            "/period/",
            headers=user1_headers,
            json={"start_date": "2025-01-01", "end_date": "2025-01-05"},
        )
        client.post(
            "/period/",
            headers=user2_headers,
            json={"start_date": "2025-01-15", "end_date": "2025-01-20"},
        )

        # Get all periods as admin
        response = client.get("/period/", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert data["count"] >= 2
        assert isinstance(data["events"], list)

    def test_get_all_periods_as_non_admin(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/period/", headers=user_headers)
        assert response.status_code == 403


class TestPeriodDateFiltering:
    def test_filter_by_start_date(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        user_headers: dict[str, str],
    ) -> None:
        # Create periods at different dates
        client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2024-12-01", "end_date": "2024-12-05"},
        )
        client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2025-02-01", "end_date": "2025-02-05"},
        )

        # Filter by start_date
        response = client.get("/period/?start_date=2025-01-01", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["start_date"] >= "2025-01-01"

    def test_filter_by_end_date(
        self,
        client: TestClient,
        admin_headers: dict[str, str],
        user_headers: dict[str, str],
    ) -> None:
        # Create periods
        client.post(
            "/period/",
            headers=user_headers,
            json={"start_date": "2024-12-01", "end_date": "2024-12-05"},
        )

        # Filter by end_date
        response = client.get("/period/?end_date=2025-01-01", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]:
            assert event["start_date"] <= "2025-01-01T00:00:00"


class TestPeriodPrediction:
    def test_get_next_period_without_cycle_state(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Users start with no cycle_state initialized, so this should return None
        response = client.get("/period/me/next/", headers=user_headers)
        assert response.status_code == 200
        assert response.json() is None

    def test_get_next_period_without_period_data(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/period/me/next/", headers=user_headers)
        assert response.status_code == 200
        assert response.json() is None

    def test_get_next_period_with_cycle_state(
        self,
        client: TestClient,
        session: Session,
        user_headers: dict[str, str],
    ) -> None:
        # Create a user and set a cycle_state
        today = datetime.now(UTC)
        last_period_start = today - timedelta(days=28)
        last_period_end = last_period_start + timedelta(days=3)
        response = client.post(
            "/period/",
            headers=user_headers,
            json={
                "start_date": last_period_start.date().isoformat(),
                "end_date": last_period_end.date().isoformat(),
            },
        )
        assert response.status_code == 200

        # Manually update the user's cycle_state to have average cycle length
        user_response = client.get("/users/me", headers=user_headers)
        user_id = user_response.json()["user_id"]
        user = session.get(models.User, user_id)
        user.cycle_state = models.Cycle(
            state=models.CycleState.STABLE,
            avg_cycle_length=28,
            avg_period_length=3,
            last_period_start=last_period_start,
            last_evaluated=datetime.now(UTC),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Now request the next period prediction
        response = client.get("/period/me/next/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data is not None
        assert data["start_date"] == today.date().isoformat()
        assert data["end_date"] == (today + timedelta(days=3)).date().isoformat()

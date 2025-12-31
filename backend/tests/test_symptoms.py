from datetime import UTC, datetime, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from tests.utils.events import create_symptom_events
from tests.utils.user import create_random_user


class TestSymptomEventCreation:
    def test_create_symptom_event(self, client: TestClient, user_headers: dict) -> None:
        """Test creating a symptom event with all fields."""
        now = datetime.now(UTC)
        response = client.post(
            "/api/symptoms/",
            headers=user_headers,
            json={
                "date": now.date().isoformat(),
                "flow_intensity": 2,  # LIGHT
                "symptoms": ["cramps", "headache"],
                "mood": ["happy", "energetic"],
                "ovulation_test": True,
                "discharge": ["clear", "stretchy"],
                "sex": ["protected"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["flow_intensity"] == 2
        assert set(data["symptoms"]) == {"cramps", "headache"}
        assert set(data["mood"]) == {"happy", "energetic"}
        assert data["ovulation_test"] is True
        assert set(data["discharge"]) == {"clear", "stretchy"}
        assert set(data["sex"]) == {"protected"}

    def test_create_symptom_event_minimal(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test creating a symptom event with minimal fields."""
        now = datetime.now(UTC)
        response = client.post(
            "/api/symptoms/",
            headers=user_headers,
            json={
                "date": now.date().isoformat(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["flow_intensity"] is None
        assert data["symptoms"] is None or data["symptoms"] == []
        assert data["mood"] is None or data["mood"] == []
        assert data["ovulation_test"] is None
        assert data["discharge"] is None or data["discharge"] == []
        assert data["sex"] is None or data["sex"] == []

    def test_create_symptom_event_with_default_date(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test creating a symptom event without providing a date."""
        response = client.post(
            "/api/symptoms/",
            headers=user_headers,
            json={"symptoms": ["bloating"]},
        )
        assert response.status_code == 200
        data = response.json()
        # Should use yesterday's date as default
        yesterday = (datetime.now(UTC) - timedelta(days=1)).date()
        assert data["date"].startswith(str(yesterday))

    def test_create_symptom_event_unauthorized(self, client: TestClient) -> None:
        """Test that creating a symptom event requires authentication."""
        response = client.post(
            "/api/symptoms/",
            json={"date": datetime.now(UTC).date().isoformat()},
        )
        assert response.status_code == 401


class TestSymptomEventRetrieval:
    def test_get_my_symptom_events(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test retrieving user's symptom events."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        # Create symptom events
        create_symptom_events(
            session,
            user,
            [
                (now - timedelta(days=5), {"flow_intensity": "heavy"}),
                (now - timedelta(days=3), {"symptoms": ["cramps"]}),
                (now - timedelta(days=1), {"mood": ["happy"]}),
            ],
        )

        response = client.get("/api/symptoms/me/", headers=user_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3
        assert len(data["events"]) == 3
        # Should be ordered by date descending (most recent first)
        dates = [event["date"] for event in data["events"]]
        assert dates == sorted(dates, reverse=True)

    def test_get_single_symptom_event(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test retrieving a single symptom event by ID."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        symptoms = create_symptom_events(
            session,
            user,
            [(now, {"flow_intensity": "heavy", "symptoms": ["cramps"]})],
        )
        symptom = symptoms[0]

        response = client.get(f"/api/symptoms/me/{symptom.pid}", headers=user_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["pid"] == symptom.pid
        assert data["flow_intensity"] == "heavy"
        assert "cramps" in data["symptoms"]

    def test_get_single_symptom_event_not_found(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test retrieving a non-existent symptom event."""
        response = client.get("/api/symptoms/me/999999", headers=user_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_symptom_events_unauthorized(self, client: TestClient) -> None:
        """Test that retrieving symptom events requires authentication."""
        response = client.get("/api/symptoms/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSymptomEventUpdate:
    def test_update_symptom_event(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test updating a symptom event."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        symptoms = create_symptom_events(
            session,
            user,
            [(now, {"flow_intensity": "heavy", "symptoms": ["cramps"]})],
        )
        symptom = symptoms[0]

        # Update the symptom event
        response = client.patch(
            f"/api/symptoms/me/{symptom.pid}",
            headers=user_headers,
            json={
                "flow_intensity": "heavy",
                "symptoms": ["cramps", "headache"],
                "mood": ["tired"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["flow_intensity"] == "heavy"
        assert set(data["symptoms"]) == {"cramps", "headache"}
        assert "tired" in data["mood"]

    def test_update_symptom_event_date(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test updating symptom event date."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        symptoms = create_symptom_events(session, user, [(now, {2})])
        symptom = symptoms[0]

        new_date = (now - timedelta(days=7)).date().isoformat()
        response = client.patch(
            f"/api/symptoms/me/{symptom.pid}",
            headers=user_headers,
            json={"date": new_date},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["date"].startswith(new_date)

    def test_update_symptom_event_not_found(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test updating a non-existent symptom event."""
        response = client.patch(
            "/api/symptoms/me/999999",
            headers=user_headers,
            json={3},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_symptom_event_partial(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test partial update of symptom event."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        symptoms = create_symptom_events(
            session,
            user,
            [
                (
                    now,
                    {
                        "flow_intensity": "heavy",
                        "symptoms": ["cramps"],
                        "mood": ["happy"],
                    },
                )
            ],
        )
        symptom = symptoms[0]

        # Update only flow_intensity
        response = client.patch(
            f"/api/symptoms/me/{symptom.pid}",
            headers=user_headers,
            json={4},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["flow_intensity"] == "heavy"
        # Other fields should remain unchanged
        assert "cramps" in data["symptoms"]
        assert "happy" in data["mood"]


class TestSymptomEventDeletion:
    def test_delete_symptom_event(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test deleting a symptom event."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        symptoms = create_symptom_events(session, user, [(now, {2})])
        symptom = symptoms[0]

        response = client.delete(f"/api/symptoms/me/{symptom.pid}", headers=user_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify the symptom event was deleted
        deleted_symptom = session.get(models.SymptomEvent, symptom.pid)
        assert deleted_symptom is None

    def test_delete_symptom_event_not_found(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test deleting a non-existent symptom event."""
        response = client.delete("/api/symptoms/me/999999", headers=user_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSymptomEventAdminAccess:
    def test_get_all_symptom_events_as_admin(
        self, client: TestClient, session: Session
    ) -> None:
        """Test admin can retrieve all symptom events."""
        admin = create_random_user(session, is_admin=True, password="password")
        user1 = create_random_user(session)
        user2 = create_random_user(session)

        now = datetime.now(UTC)
        # Create symptom events for multiple users
        create_symptom_events(session, user1, [(now - timedelta(days=5), {2})])
        create_symptom_events(
            session, user2, [(now - timedelta(days=3), {"symptoms": ["cramps"]})]
        )

        admin_token = client.post(
            "/api/auth/token",
            data={"username": admin.username, "password": "password"},
        ).json()["access_token"]

        response = client.get(
            "/api/symptoms/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 2
        # Should include events from both users
        user_ids = {event["user_id"] for event in data["events"]}
        assert user1.user_id in user_ids
        assert user2.user_id in user_ids

    def test_get_all_symptom_events_as_non_admin(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test non-admin cannot retrieve all symptom events."""
        response = client.get("/api/symptoms/", headers=user_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSymptomEventDateFiltering:
    def test_filter_by_start_date(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test filtering symptom events by start date."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        # Create symptom events across different dates
        create_symptom_events(
            session,
            user,
            [
                (now - timedelta(days=10), {2}),
                (now - timedelta(days=5), {"symptoms": ["cramps"]}),
                (now - timedelta(days=2), {"mood": ["happy"]}),
            ],
        )

        # Filter for events from the last 7 days
        start_date = (now - timedelta(days=7)).date().isoformat()
        response = client.get(
            f"/api/symptoms/me/?start_date={start_date}",
            headers=user_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        # Only events from days 5 and 2 should be included
        for event in data["events"]:
            event_date = datetime.fromisoformat(event["date"]).date()
            assert event_date >= datetime.fromisoformat(start_date).date()

    def test_filter_by_end_date(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test filtering symptom events by end date."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        # Create symptom events across different dates
        create_symptom_events(
            session,
            user,
            [
                (now - timedelta(days=10), {2}),
                (now - timedelta(days=5), {"symptoms": ["cramps"]}),
                (now - timedelta(days=2), {"mood": ["happy"]}),
            ],
        )

        # Filter for events up to 6 days ago
        end_date = (now - timedelta(days=6)).date().isoformat()
        response = client.get(
            f"/api/symptoms/me/?end_date={end_date}",
            headers=user_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        # Only event from day 10 should be included
        for event in data["events"]:
            event_date = datetime.fromisoformat(event["date"]).date()
            assert event_date <= datetime.fromisoformat(end_date).date()

    def test_filter_by_date_range(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test filtering symptom events by date range."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        # Create symptom events across different dates
        create_symptom_events(
            session,
            user,
            [
                (now - timedelta(days=15), {2}),
                (now - timedelta(days=10), {"symptoms": ["cramps"]}),
                (now - timedelta(days=5), {"mood": ["happy"]}),
                (now - timedelta(days=2), {3}),
            ],
        )

        # Filter for events between 12 and 4 days ago
        start_date = (now - timedelta(days=12)).date().isoformat()
        end_date = (now - timedelta(days=4)).date().isoformat()
        response = client.get(
            f"/api/symptoms/me/?start_date={start_date}&end_date={end_date}",
            headers=user_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        # Only events from days 10 and 5 should be included
        for event in data["events"]:
            event_date = datetime.fromisoformat(event["date"]).date()
            assert datetime.fromisoformat(start_date).date() <= event_date
            assert event_date <= datetime.fromisoformat(end_date).date()


class TestSymptomEventPagination:
    def test_pagination_with_limit(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test pagination with limit parameter."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        # Create 10 symptom events
        events_data = [(now - timedelta(days=i), {2}) for i in range(10)]
        create_symptom_events(session, user, events_data)

        # Request only 5 events
        response = client.get("/api/symptoms/me/?limit=5", headers=user_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["events"]) == 5
        assert data["count"] == 5

    def test_pagination_with_offset(
        self, client: TestClient, user_headers: dict, session: Session
    ) -> None:
        """Test pagination with offset parameter."""
        user = session.exec(
            models.select(models.User).where(
                models.User.username == user_headers.get("test_user")
            )
        ).first()
        assert user is not None

        now = datetime.now(UTC)
        # Create 10 symptom events
        events_data = [(now - timedelta(days=i), {2}) for i in range(10)]
        create_symptom_events(session, user, events_data)

        # Get first page
        response1 = client.get("/api/symptoms/me/?limit=5", headers=user_headers)
        first_page = response1.json()["events"]

        # Get second page with offset
        response2 = client.get("/api/symptoms/me/?limit=5&offset=5", headers=user_headers)
        second_page = response2.json()["events"]

        # Verify pages don't overlap
        first_ids = {event["pid"] for event in first_page}
        second_ids = {event["pid"] for event in second_page}
        assert len(first_ids.intersection(second_ids)) == 0

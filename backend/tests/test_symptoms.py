from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from tests.utils.auth import get_user_headers
from tests.utils.events import create_symptom_events
from tests.utils.user import create_random_user


class TestSymptomEventCreation:
    def test_create_symptom_event(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        now = datetime.now(UTC)
        response = client.post(
            "/symptoms/",
            headers=user_headers,
            json={
                "date": now.date().isoformat(),
                "flow_intensity": "2",  # LIGHT
                "symptoms": ["cramps", "headache"],
                "mood": ["happy", "energetic"],
                "ovulation_test": True,
                "discharge": ["clear", "stretchy"],
                "sex": ["protected"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["flow_intensity"] == "2"
        assert set(data["symptoms"]) == {"cramps", "headache"}
        assert set(data["mood"]) == {"happy", "energetic"}
        assert data["ovulation_test"] is True
        assert set(data["discharge"]) == {"clear", "stretchy"}
        assert set(data["sex"]) == {"protected"}

    def test_create_symptom_event_only_date(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        now = datetime.now(UTC)
        response = client.post(
            "/symptoms/",
            headers=user_headers,
            json={"date": now.date().isoformat()},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["flow_intensity"] is None
        assert data["symptoms"] is None or data["symptoms"] == []
        assert data["mood"] is None or data["mood"] == []
        assert data["ovulation_test"] is None
        assert data["discharge"] is None or data["discharge"] == []
        assert data["sex"] is None or data["sex"] == []

    def test_create_symptom_event_with_default_date(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        response = client.post(
            "/symptoms/",
            headers=user_headers,
            json={"symptoms": ["bloating"]},
        )
        assert response.status_code == 200
        data = response.json()
        # Should default to today's date
        today_str = datetime.now(UTC).date().isoformat()
        assert data["date"].startswith(today_str)
        assert "bloating" in data["symptoms"]

    def test_create_symptom_event_unauthorized(self, client: TestClient) -> None:
        """Test that creating a symptom event requires authentication."""
        response = client.post("/symptoms/")
        assert response.status_code == 401


class TestSymptomEventRetrieval:
    def test_get_my_symptom_events(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        now = datetime.now(UTC)
        symptoms = [
            {
                "date": (now - timedelta(days=5)).date().isoformat(),
                "flow_intensity": "4",
            },
            {
                "date": (now - timedelta(days=3)).date().isoformat(),
                "symptoms": ["cramps"],
            },
            {"date": (now - timedelta(days=1)).date().isoformat(), "mood": ["happy"]},
        ]
        for s in symptoms:
            response = client.post(
                "/symptoms/",
                headers=user_headers,
                json=s,
            )
        response = client.get("/symptoms/me/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["events"]["symptoms"]) == 3

    def test_get_single_symptom_event(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        create_response = client.post(
            "/symptoms/",
            headers=user_headers,
            json={"flow_intensity": "4", "symptoms": ["cramps"]},
        )
        s_id = create_response.json()["pid"]
        response = client.get(f"/symptoms/me/{s_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["pid"] == s_id
        assert data["flow_intensity"] == "4"
        assert data["symptoms"] == ["cramps"]
        assert "cramps" in data["symptoms"]

    def test_get_single_symptom_event_not_found(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        """Test retrieving a non-existent symptom event."""
        response = client.get("/symptoms/me/999999", headers=user_headers)
        assert response.status_code == 404

    def test_get_symptom_events_unauthorized(self, client: TestClient) -> None:
        """Test that retrieving symptom events requires authentication."""
        response = client.get("/symptoms/me/")
        assert response.status_code == 401


class TestSymptomEventUpdate:
    def test_update_symptom_event(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        create_response = client.post(
            "/symptoms/",
            headers=user_headers,
            json={"flow_intensity": "4", "symptoms": ["cramps"]},
        )
        s_id = create_response.json()["pid"]

        # Update the symptom event
        response = client.patch(
            f"/symptoms/me/{s_id}",
            headers=user_headers,
            json={
                "date": "2025-01-15",
                "flow_intensity": "0",
                "symptoms": ["cramps", "headache"],
                "mood": ["tired"],
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "2025-01-15" in data["date"]
        assert data["flow_intensity"] == "0"
        assert data["symptoms"] == ["cramps", "headache"]
        assert "tired" in data["mood"]

    def test_update_symptom_event_not_found(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        response = client.patch("/symptoms/me/999999", headers=user_headers, json={})
        assert response.status_code == 404


class TestSymptomEventDeletion:
    def test_delete_symptom_event(
        self, client: TestClient, user_headers: dict[str, str], session: Session
    ) -> None:
        create_response = client.post(
            "/symptoms/",
            headers=user_headers,
            json={"flow_intensity": "4", "symptoms": ["cramps"]},
        )
        s_id = create_response.json()["pid"]

        response = client.delete(f"/symptoms/me/{s_id}", headers=user_headers)
        data = response.json()
        assert data["resource_type"] == "symptom"
        assert data["resource_id"] == str(s_id)

        # Verify the symptom event was deleted
        assert session.get(models.SymptomEvent, s_id) is None

    def test_delete_symptom_event_not_found(
        self, client: TestClient, user_headers: dict[str, str]
    ) -> None:
        """Test deleting a non-existent symptom event."""
        response = client.delete("/symptoms/me/999999", headers=user_headers)
        assert response.status_code == 404


class TestSymptomEventAdminAccess:
    def test_get_all_symptom_events_as_admin(
        self,
        client: TestClient,
        session: Session,
        admin_headers: dict[str, str],
    ) -> None:
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        now = datetime.now(UTC)

        # Create symptom events for multiple users
        create_symptom_events(
            session, user1, [{"date": (now - timedelta(days=2)), "flow_intensity": "3"}]
        )
        create_symptom_events(
            session, user2, [{"date": (now - timedelta(days=3)), "symptoms": ["cramps"]}]
        )

        # Check for the readings as admin
        response = client.get("/symptoms/", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] >= 2
        # Should include events from both users
        user_ids = {event["user_id"] for event in data["events"]["symptoms"]}
        assert user1.user_id in user_ids
        assert user2.user_id in user_ids

    def test_get_all_symptom_events_as_non_admin(
        self, client: TestClient, user_headers: dict
    ) -> None:
        """Test non-admin cannot retrieve all symptom events."""
        response = client.get("/symptoms/", headers=user_headers)
        assert response.status_code == 403


class TestSymptomEventDateFiltering:
    def test_filter_by_start_date(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)
        now = datetime.now(UTC)
        # Create symptom events across different dates
        create_symptom_events(
            session,
            user,
            [
                {"date": (now - timedelta(days=10)), "flow_intensity": "2"},
                {"date": (now - timedelta(days=5)), "symptoms": ["cramps"]},
                {"date": (now - timedelta(days=2)), "mood": ["happy"]},
            ],
        )

        # Filter for events from the last 7 days
        start_date = (now - timedelta(days=7)).date().isoformat()
        response = client.get(
            f"/symptoms/me/?start_date={start_date}",
            headers=user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        # Only events from days 5 and 2 should be included
        for event in data["events"]["symptoms"]:
            event_date = datetime.fromisoformat(event["date"]).date()
            assert event_date >= datetime.fromisoformat(start_date).date()

    def test_filter_by_end_date(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)
        now = datetime.now(UTC)
        # Create symptom events across different dates
        create_symptom_events(
            session,
            user,
            [
                {"date": (now - timedelta(days=10)), "flow_intensity": "2"},
                {"date": (now - timedelta(days=5)), "symptoms": ["cramps"]},
                {"date": (now - timedelta(days=2)), "mood": ["happy"]},
            ],
        )

        # Filter for events up to 6 days ago
        end_date = (now - timedelta(days=6)).date().isoformat()
        response = client.get(
            f"/symptoms/me/?end_date={end_date}",
            headers=user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        # Only event from day 10 should be included
        for event in data["events"]["symptoms"]:
            event_date = datetime.fromisoformat(event["date"]).date()
            assert event_date <= datetime.fromisoformat(end_date).date()

    def test_filter_by_date_range(self, client: TestClient, session: Session) -> None:
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)
        now = datetime.now(UTC)
        # Create symptom events across different dates
        create_symptom_events(
            session,
            user,
            [
                {"date": (now - timedelta(days=15)), "flow_intensity": "2"},
                {"date": (now - timedelta(days=10)), "symptoms": ["cramps"]},
                {"date": (now - timedelta(days=5)), "mood": ["happy"]},
                {"date": (now - timedelta(days=2)), "flow_intensity": "3"},
            ],
        )
        # Filter for events between 12 and 4 days ago
        start_date = (now - timedelta(days=12)).date().isoformat()
        end_date = (now - timedelta(days=4)).date().isoformat()
        response = client.get(
            f"/symptoms/me/?start_date={start_date}&end_date={end_date}",
            headers=user_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        # Only events from days 10 and 5 should be included
        for event in data["events"]["symptoms"]:
            event_date = datetime.fromisoformat(event["date"]).date()
            assert datetime.fromisoformat(start_date).date() <= event_date
            assert event_date <= datetime.fromisoformat(end_date).date()

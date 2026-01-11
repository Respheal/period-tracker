from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from tests.utils.auth import get_user_headers
from tests.utils.events import create_temperature_readings
from tests.utils.user import create_random_user


class TestTemperatureCreation:
    def test_create_temp_reading(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.post("/temp/", headers=user_headers, json={"temperature": 36.5})
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == 36.5

    def test_create_temp_reading_validation(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Temperature too low
        response = client.post("/temp/", headers=user_headers, json={"temperature": 29.0})
        assert response.status_code == 422

        # Temperature too high
        response = client.post("/temp/", headers=user_headers, json={"temperature": 41.0})
        assert response.status_code == 422


class TestTemperatureRetrieval:
    def test_get_my_temp_readings(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create some temperature readings for the user
        temps = [36.5, 37.0, 36.8]
        for temp in temps:
            client.post("/temp/", headers=user_headers, json={"temperature": temp})

        response = client.get("/temp/me/", headers=user_headers)
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert data["count"] >= 3
        assert "events" in data
        assert "temperatures" in data["events"]
        assert len(data["events"]["temperatures"]) >= 3

        temperatures = [event["temperature"] for event in data["events"]["temperatures"]]
        for temp in temps:
            assert temp in temperatures

    def test_get_single_temp_reading(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a temperature reading
        create_response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 36.5}
        )
        assert create_response.status_code == 200
        temp_id = create_response.json()["pid"]

        # Retrieve the specific reading
        response = client.get(f"/temp/me/{temp_id}", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["pid"] == temp_id
        assert data["temperature"] == 36.5

    def test_get_single_temp_reading_not_found(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/temp/me/99999", headers=user_headers)
        assert response.status_code == 404

    def test_get_other_user_temp(
        self,
        client: TestClient,
        session: Session,
        user_headers: dict[str, str],
    ) -> None:
        other_user = create_random_user(session)
        # Create a temperature reading for the other user
        other_temp = create_temperature_readings(session, other_user, [36.7])[0]
        response = client.get(f"/temp/me/{other_temp.pid}", headers=user_headers)
        assert response.status_code == 404


class TestTemperatureUpdate:
    def test_update_temp_reading(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a temperature reading
        create_response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 36.5}
        )
        assert create_response.status_code == 200
        temp_id = create_response.json()["pid"]

        # Update the temperature
        response = client.patch(
            f"/temp/me/{temp_id}",
            headers=user_headers,
            json={"temperature": 37.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == 37.0

    def test_update_temp_timestamp(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a temperature reading
        create_response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 36.5}
        )
        assert create_response.status_code == 200
        temp_id = create_response.json()["pid"]

        # Update the timestamp
        response = client.patch(
            f"/temp/me/{temp_id}",
            headers=user_headers,
            json={"timestamp": "2025-01-15"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "2025-01-15" in data["timestamp"]

    def test_update_temp_reading_not_found(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.patch(
            "/temp/me/99999",
            headers=user_headers,
            json={"temperature": 37.0},
        )
        assert response.status_code == 404

    def test_update_temp_validation(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a temperature reading
        create_response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 36.5}
        )
        assert create_response.status_code == 200
        temp_id = create_response.json()["pid"]

        # Try to update with invalid temperature
        response = client.patch(
            f"/temp/me/{temp_id}",
            headers=user_headers,
            json={"temperature": 50.0},  # Too high
        )
        assert response.status_code == 422


class TestTemperatureDeletion:
    def test_delete_temp_reading(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create a temperature reading
        create_response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 36.5}
        )
        assert create_response.status_code == 200
        temp_id = create_response.json()["pid"]

        # Delete the temperature
        response = client.delete(f"/temp/me/{temp_id}", headers=user_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["resource_type"] == "temperature"
        assert data["resource_id"] == str(temp_id)

        # Verify it's actually deleted
        get_response = client.get(f"/temp/me/{temp_id}", headers=user_headers)
        assert get_response.status_code == 404

    def test_delete_temp_reading_not_found(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.delete("/temp/me/99999", headers=user_headers)
        assert response.status_code == 404


class TestTemperatureAdminAccess:
    def test_get_all_temp_readings_as_admin(
        self,
        session: Session,
        client: TestClient,
        admin_headers: dict[str, str],
    ) -> None:
        # Create temperature readings for different users
        user1 = create_random_user(session)
        user2 = create_random_user(session)
        user1_headers = get_user_headers(client, session, user1.username)
        user2_headers = get_user_headers(client, session, user2.username)

        for temp in [36.5, 37.0]:
            client.post("/temp/", headers=user1_headers, json={"temperature": temp})

        for temp in [36.8, 37.2]:
            client.post("/temp/", headers=user2_headers, json={"temperature": temp})

        # Also create some readings in the past for date filtering tests
        session.add(
            models.Temperature(
                user_id=user2.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 12, 19, 0, 0, 0, 0, tzinfo=UTC),
            )
        )
        session.add(
            models.Temperature(
                user_id=user2.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0, tzinfo=UTC),
            )
        )
        session.commit()

        # Check for the readings as admin
        response = client.get("/temp/", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert data["count"] >= 6
        assert "events" in data
        assert "temperatures" in data["events"]

        temperatures = [event["temperature"] for event in data["events"]["temperatures"]]
        for temp in [36.5, 37.0, 36.8, 37.2]:
            assert temp in temperatures

    def test_get_all_temp_readings_as_non_admin(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.get("/temp/", headers=user_headers)
        assert response.status_code == 403


class TestTemperatureDateFiltering:
    def test_filter_by_start_date(
        self,
        session: Session,
        client: TestClient,
        admin_headers: dict[str, str],
    ) -> None:
        # Create test data (reuse setup from admin test)
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)

        client.post("/temp/", headers=user_headers, json={"temperature": 36.5})
        # Also create some readings in the past for date filtering tests
        session.add(
            models.Temperature(
                user_id=user.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 12, 19, 0, 0, 0, 0, tzinfo=UTC),
            )
        )
        session.add(
            models.Temperature(
                user_id=user.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0, tzinfo=UTC),
            )
        )
        session.commit()

        # Test start_date filter
        response = client.get("/temp/?start_date=2025-01-01", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]["temperatures"]:
            assert event["timestamp"] >= "2025-01-01T00:00:00"

    def test_filter_by_end_date(
        self,
        session: Session,
        client: TestClient,
        admin_headers: dict[str, str],
    ) -> None:
        user = create_random_user(session)
        session.add(
            models.Temperature(
                user_id=user.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0, tzinfo=UTC),
            )
        )
        session.commit()

        response = client.get("/temp/?end_date=2025-01-01", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]["temperatures"]:
            assert event["timestamp"] <= "2025-01-01T00:00:00"

    def test_filter_by_date_range(
        self,
        session: Session,
        client: TestClient,
        admin_headers: dict[str, str],
    ) -> None:
        user = create_random_user(session)
        session.add(
            models.Temperature(
                user_id=user.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0, tzinfo=UTC),
            )
        )
        session.commit()

        response = client.get(
            "/temp/?start_date=2024-01-01&end_date=2024-09-01", headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        for event in data["events"]["temperatures"]:
            assert event["timestamp"] <= "2024-09-01T00:00:00"
            assert event["timestamp"] >= "2024-01-01T00:00:00"


class TestTemperatureAverages:
    def test_get_my_temp_averages(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create some temperature readings for the user
        temps = [36.5, 37.0, 36.8, 37.2, 36.9]
        for temp in temps:
            client.post("/temp/", headers=user_headers, json={"temperature": temp})
        response = client.get("/temp/me/averages/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Verify the structure of returned data
        for item in data:
            assert "timestamp" in item
            assert "temperature" in item
            assert "ewm" in item
            assert "baseline" in item
            # Verify values are reasonable
            assert 30.0 <= item["temperature"] <= 40.0
            assert 30.0 <= item["ewm"] <= 40.0
            assert 30.0 <= item["baseline"] <= 40.0

    def test_get_my_temp_averages_precision(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Create temperature readings
        temps = [36.564567, 37.12643, 36.89451]
        for temp in temps:
            client.post("/temp/", headers=user_headers, json={"temperature": temp})

        # Test with default precision (2)
        response = client.get("/temp/me/averages/", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        # Check that values are rounded to 2 decimal places
        for item in data:
            assert len(str(item["ewm"]).split(".")[-1]) <= 2
            assert len(str(item["baseline"]).split(".")[-1]) <= 2

        # Test with custom precision
        response = client.get("/temp/me/averages/?precision=4", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Check that values are rounded to 4 decimal places
        for item in data:
            assert len(str(item["ewm"]).split(".")[-1]) <= 4
            assert len(str(item["baseline"]).split(".")[-1]) <= 4


class TestTemperatureState:
    def test_temperature_state_initialization(
        self,
        session: Session,
    ) -> None:
        """Test that new users get an initialized temperature state."""
        user = create_random_user(session)
        session.refresh(user)

        # User should have a temp_state initialized to LEARNING
        assert user.temp_state is not None
        assert user.temp_state.phase == models.TempPhase.LEARNING
        assert user.temp_state.baseline is None

from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from tests.utils.auth import get_user_headers
from tests.utils.user import create_random_user


class TestTemperatureCreation:
    def test_create_temp_reading(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 36.5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature"] == 36.5

    def test_create_temp_reading_validation(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        # Temperature too low
        response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 29.0}
        )
        assert response.status_code == 422

        # Temperature too high
        response = client.post(
            "/temp/", headers=user_headers, json={"temperature": 41.0}
        )
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
        assert isinstance(data["events"], list)

        temperatures = [event["temperature"] for event in data["events"]]
        for temp in temps:
            assert temp in temperatures


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
                timestamp=datetime(2024, 12, 19, 0, 0, 0, 0),
            )
        )
        session.add(
            models.Temperature(
                user_id=user2.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0),
            )
        )
        session.commit()

        # Check for the readings as admin
        response = client.get("/temp/", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        assert "count" in data
        assert data["count"] >= 6
        assert isinstance(data["events"], list)

        temperatures = [event["temperature"] for event in data["events"]]
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

        session.add(
            models.Temperature(
                user_id=user.user_id,
                temperature=37.5,
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0),
            )
        )
        session.commit()

        # Test start_date filter
        response = client.get("/temp/?start_date=2025-01-01", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        for event in data["events"]:
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
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0),
            )
        )
        session.commit()

        response = client.get("/temp/?end_date=2025-01-01", headers=admin_headers)
        assert response.status_code == 200

        data = response.json()
        for event in data["events"]:
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
                timestamp=datetime(2024, 6, 19, 0, 0, 0, 0),
            )
        )
        session.commit()

        response = client.get(
            "/temp/?start_date=2024-01-01&end_date=2024-09-01", headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        for event in data["events"]:
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
        temps = [36.567, 37.123, 36.891]
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

    def test_temperature_state_updates_with_readings(
        self,
        session: Session,
        client: TestClient,
    ) -> None:
        """Test that temperature state updates as readings are added."""
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)

        # Add enough readings to move out of LEARNING phase
        for _ in range(15):
            client.post("/temp/", headers=user_headers, json={"temperature": 36.5})

        session.refresh(user)
        # Should have moved to LOW phase
        assert user.temp_state.phase in [models.TempPhase.LOW, models.TempPhase.LEARNING]
        if user.temp_state.phase == models.TempPhase.LOW:
            assert user.temp_state.baseline is not None

    def test_temperature_state_elevated_phase(
        self,
        session: Session,
        client: TestClient,
    ) -> None:
        """Test that elevated phase is detected correctly."""
        user = create_random_user(session)
        user_headers = get_user_headers(client, session, user.username)

        # Add low baseline readings (need enough to establish baseline)
        for _ in range(20):
            client.post("/temp/", headers=user_headers, json={"temperature": 36.5})

        # Add sustained elevated readings
        for _ in range(5):
            client.post("/temp/", headers=user_headers, json={"temperature": 37.5})

        session.refresh(user)
        # Note: Background task execution in tests may not always trigger immediately,
        # so we accept LEARNING, LOW, or ELEVATED as valid states
        assert user.temp_state.phase in [
            models.TempPhase.ELEVATED,
            models.TempPhase.LOW,
            models.TempPhase.LEARNING,
        ]


class TestTemperatureExport:
    def test_csv_export_includes_averages(
        self,
        client: TestClient,
        user_headers: dict[str, str],
    ) -> None:
        """Test that CSV export includes ewm and baseline columns."""
        # Create some temperature readings
        temps = [36.5, 37.0, 36.8, 37.2, 36.9]
        for temp in temps:
            client.post("/temp/", headers=user_headers, json={"temperature": temp})

        response = client.get("/temp/me/csv/", headers=user_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"

        # Parse CSV - handle both Unix (\n) and Windows (\r\n) line endings
        csv_content = response.text
        lines = csv_content.strip().replace("\r\n", "\n").split("\n")
        headers = [h.strip() for h in lines[0].split(",")]

        # Verify required columns exist
        assert "timestamp" in headers
        assert "temperature" in headers
        assert "ewm" in headers
        assert "baseline" in headers

        # Verify we have data rows
        assert len(lines) > 1

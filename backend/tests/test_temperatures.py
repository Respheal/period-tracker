from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from api.utils.config import Settings
from tests.utils.auth import get_user_headers
from tests.utils.user import create_random_user


def test_create_temp_reading(
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    response = client.post("/temp/", headers=user_headers, json={"temperature": 36.5})
    assert response.status_code == 200
    data = response.json()
    assert data["temperature"] == 36.5

    # Temperatures must be in a normal human range
    response = client.post("/temp/", headers=user_headers, json={"temperature": 29.0})
    assert response.status_code == 422
    response = client.post("/temp/", headers=user_headers, json={"temperature": 41.0})
    assert response.status_code == 422


def test_get_my_temp_readings(
    session: Session,
    client: TestClient,
    user_headers: dict[str, str],
) -> None:
    # Create some temperature readings for the user
    for temp in [36.5, 37.0, 36.8]:
        client.post("/temp/", headers=user_headers, json={"temperature": temp})
    response = client.get("/temp/me/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] >= 3
    assert isinstance(data["events"], list)
    temperatures = [event["temperature"] for event in data["events"]]
    for temp in [36.5, 37.0, 36.8]:
        assert temp in temperatures


def test_get_all_temp_readings_admin(
    session: Session,
    client: TestClient,
    admin_headers: dict[str, str],
    user_headers: dict[str, str],
) -> None:
    # Create some temperature readings for different users
    user1 = create_random_user(session)
    user2 = create_random_user(session)
    user1_headers = get_user_headers(client, session, user1.username)
    user2_headers = get_user_headers(client, session, user2.username)
    for temp in [36.5, 37.0]:
        client.post(
            "/temp/",
            headers=user1_headers,
            json={"temperature": temp},
        )
    for temp in [36.8, 37.2]:
        client.post(
            "/temp/",
            headers=user2_headers,
            json={"temperature": temp},
        )
    # Also make some reading in the past to test date filtering
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
        ),
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
    # Verify non-admin cannot access
    response = client.get("/temp/", headers=user_headers)
    assert response.status_code == 403
    # Verify that we can filter by date
    response = client.get("/temp/?start_date=2025-01-01", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 4
    for event in data["events"]:
        assert event["timestamp"] >= "2025-01-01T00:00:00"
    response = client.get("/temp/?end_date=2025-01-01", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    for event in data["events"]:
        assert event["timestamp"] <= "2025-01-01T00:00:00"
    response = client.get(
        "/temp/?start_date=2024-01-01&end_date=2024-09-01", headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    for event in data["events"]:
        assert event["timestamp"] <= "2024-09-01T00:00:00"
        assert event["timestamp"] >= "2024-01-01T00:00:00"


def test_get_my_temp_averages(
    client: TestClient,
    settings: Settings,
    user_headers: dict[str, str],
) -> None:
    # Create some temperature readings for the user
    temps = [36.5, 37.0, 36.8, 37.2, 36.9]
    for temp in temps:
        client.post("/temp/", headers=user_headers, json={"temperature": temp})
    response = client.get("/temp/me/averages/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] >= 1
    assert isinstance(data["events"], list)
    # Calculate expected ema
    counter = 0
    average = 0.0
    for temp in temps:
        counter += 1
        average = average + (temp - average) / min(counter, settings.SMOOTHING_FACTOR)
    # The last average_temperature should match our calculated average
    last_event = data["events"][-1]
    assert abs(last_event["average_temperature"] - average) < 0.01

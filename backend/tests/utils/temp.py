from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from api.db import models


def create_temperature_readings(
    session: Session,
    user: models.User,
    temps: list[float],
    start_date: datetime | None = None,
) -> list[models.Temperature]:
    """Helper function to create temperature readings for testing."""
    if start_date is None:
        start_date = datetime.now(UTC)
    readings = []
    for i, temp in enumerate(temps):
        timestamp = start_date - timedelta(days=len(temps) - i - 1)
        reading = models.Temperature(
            user_id=user.user_id,
            temperature=temp,
            timestamp=timestamp,
        )
        session.add(reading)
        readings.append(reading)

    session.commit()
    return readings

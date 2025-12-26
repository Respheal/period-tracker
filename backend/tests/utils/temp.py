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


def create_period_events(
    session: Session,
    user: models.User,
    periods: list[tuple[datetime, datetime | None]],
) -> list[models.Period]:
    """Helper function to create period events for testing."""
    events = []
    for start_date, end_date in periods:
        event = models.Period(
            user_id=user.user_id,
            start_date=start_date,
            end_date=end_date,
            duration=(end_date - start_date).days if end_date else None,
        )
        session.add(event)
        events.append(event)

    session.commit()
    return events

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlmodel import Session

from api.db import models
from api.db.crud import period as period_crud
from api.db.crud import symptoms as symptom_crud
from api.db.crud import temperature as temp_crud


def create_temperature_readings(
    session: Session,
    user: models.User,
    temps: list[float],
    start_date: datetime | None = None,
) -> list[models.Temperature]:
    """
    Helper function to create temperature readings for testing. Temperatures are created
    starting from start_date going backwards in time as far as the length of temps.
    """
    if start_date is None:
        start_date = datetime.now(UTC)
    readings = []
    for i, temp in enumerate(temps):
        db_temp = temp_crud.create_temp_reading(
            session,
            models.CreateTempRead(
                user_id=user.user_id,
                temperature=temp,
                timestamp=start_date - timedelta(days=len(temps) - i - 1),
            ),
        )
        readings.append(db_temp)
    return readings


def create_period_events(
    session: Session,
    user: models.User,
    periods: list[tuple[datetime, datetime | None]],
) -> list[models.Period]:
    """Helper function to create period events for testing."""
    events = []
    for start_date, end_date in periods:
        db_period = period_crud.create_period_event(
            session,
            models.CreatePeriod(
                user_id=user.user_id,
                start_date=start_date,
                end_date=end_date,
                duration=(end_date - start_date).days if end_date else None,
            ),
        )
        events.append(db_period)
    return events


def create_symptom_events(
    session: Session,
    user: models.User,
    symptoms: list[dict[str, Any]],
) -> list[models.SymptomEvent]:
    """Helper function to create symptom events for testing."""
    events = []
    for symptom in symptoms:
        db_symptom = symptom_crud.create_symptom_event(
            session,
            models.CreateSymptomEvent(
                user_id=user.user_id,
                date=symptom.get("date", None),
                flow_intensity=symptom.get("flow_intensity", None),
                symptoms=symptom.get("symptoms", None),
                mood=symptom.get("mood", None),
                ovulation_test=symptom.get("ovulation_test", None),
                discharge=symptom.get("discharge", None),
                sex=symptom.get("sex", None),
            ),
        )
        events.append(db_symptom)
    return events

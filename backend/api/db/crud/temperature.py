from datetime import datetime
from typing import Sequence

from sqlmodel import Session, desc, select

from api.db import models
from api.db.crud import user as user_crud
from api.utils.config import settings
from api.utils.stats import evaluate_temperature_state


def create_temp_reading(
    session: Session, reading: models.CreateTempRead
) -> models.Temperature:
    db_reading = models.Temperature.model_validate(reading)
    session.add(db_reading)
    session.commit()
    session.refresh(db_reading)
    return db_reading


def get_temp_readings(
    session: Session,
    user_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    order: str = "desc",
    offset: int = 0,
    limit: int = 100,
) -> Sequence[models.Temperature]:
    # By default, return the most recent 100 readings
    statement = select(models.Temperature)
    if user_id:
        statement = statement.where(models.Temperature.user_id == user_id)
    if start_date:
        statement = statement.where(models.Temperature.timestamp >= start_date)
    if end_date:
        statement = statement.where(models.Temperature.timestamp <= end_date)
    if order == "desc":
        statement = statement.order_by(desc(models.Temperature.timestamp))
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def get_temp_state(
    session: Session,
    user_id: str,
) -> models.TemperatureState | None:
    return session.exec(
        select(models.TemperatureState).where(models.TemperatureState.user_id == user_id)
    ).first()


def update_temperature_state(session: Session, user_id: str) -> None:
    readings = get_temp_readings(
        session=session, user_id=user_id, limit=settings.BASELINE_SPAN_DAYS
    )
    prev_state = get_temp_state(session=session, user_id=user_id)
    new_state = evaluate_temperature_state(
        temperatures=readings, previous_state=prev_state
    )
    user_crud.update_temp_state(session=session, user_id=user_id, new_state=new_state)

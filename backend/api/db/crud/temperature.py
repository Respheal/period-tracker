from datetime import datetime
from typing import Sequence

from sqlmodel import Session, desc, select

from api.db import models


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
    statement = select(models.Temperature)
    if user_id:
        statement = statement.where(models.Temperature.user_id == user_id)
    if start_date:
        statement = statement.where(models.Temperature.timestamp >= start_date)
    if end_date:
        statement = statement.where(models.Temperature.timestamp <= end_date)
    if order == "desc":
        statement = statement.order_by(desc(models.Temperature.timestamp))
    return session.exec(statement.offset(offset).limit(limit)).all()

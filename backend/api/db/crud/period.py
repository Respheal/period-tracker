from datetime import datetime, timedelta
from typing import Sequence

from sqlmodel import Session, desc, select

from api.db import models
from api.db.crud import temperature as temp_crud
from api.utils.dependencies import get_settings
from api.utils.stats import (
    compute_luteal_length,
    detect_elevated_phase_start,
    is_valid_luteal_length,
)


def create_period_event(session: Session, period: models.CreatePeriod) -> models.Period:
    db_period = models.Period.model_validate(period)
    session.add(db_period)
    session.commit()
    session.refresh(db_period)
    return db_period


def get_periods(
    session: Session,
    user_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    order: str = "desc",
    offset: int = 0,
    limit: int = 24,
) -> Sequence[models.Period]:
    # By default, return the most recent 100 readings
    statement = select(models.Period)
    if user_id:
        statement = statement.where(models.Period.user_id == user_id)
    if start_date:
        statement = statement.where(models.Period.start_date >= start_date)
    if end_date:
        statement = statement.where(models.Period.start_date <= end_date)
    if order == "desc":
        statement = statement.order_by(desc(models.Period.start_date))
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def update_luteal_length(session: Session, period: models.Period) -> None:
    settings = get_settings()
    lookback_date = period.start_date - timedelta(settings.MAX_LOOKBACK_DAYS)
    temperatures = temp_crud.get_temp_readings(
        session, period.user_id, start_date=lookback_date, end_date=period.start_date
    )
    elevated_start = detect_elevated_phase_start(temperatures, period)
    if elevated_start:
        luteal_length = compute_luteal_length(elevated_start, period.start_date)
        if is_valid_luteal_length(luteal_length):
            period.luteal_length = luteal_length
            session.add(period)
            session.commit()

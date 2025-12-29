from datetime import UTC, datetime, time, timedelta
from typing import Sequence

from sqlmodel import Session, desc, select

from api.db import models
from api.db.crud import temperature as temp_crud
from api.utils.dependencies import get_settings
from api.utils.stats import (
    compute_luteal_length,
    detect_elevated_phase_start,
    evaluate_cycle_state,
    is_valid_luteal_length,
)


def create_period_event(session: Session, period: models.CreatePeriod) -> models.Period:
    db_period = models.Period.model_validate(period)
    session.add(db_period)
    session.commit()
    session.refresh(db_period)
    return db_period


def get_single_period(
    session: Session,
    period_id: int,
    user_id: str | None = None,
) -> models.Period | None:
    if user_id is None:  # pragma: no cover
        return session.get(models.Period, period_id)
    return session.exec(
        select(models.Period).where(
            models.Period.pid == period_id,
            models.Period.user_id == user_id,
        )
    ).first()


def update_period(
    session: Session, period: models.Period, data: models.PeriodUpdate
) -> models.Period:
    period_data = data.model_dump(exclude_unset=True)
    # Convert date strings to datetime objects
    if "start_date" in period_data:
        min_date = datetime.strptime(period_data["start_date"], "%Y-%m-%d").replace(
            tzinfo=UTC
        )
        period_data["start_date"] = datetime.combine(min_date, time.min, tzinfo=UTC)
    if "end_date" in period_data and period_data["end_date"] is not None:
        max_date = datetime.strptime(period_data["end_date"], "%Y-%m-%d").replace(
            tzinfo=UTC
        )
        period_data["end_date"] = datetime.combine(max_date, time.max, tzinfo=UTC)
    period.sqlmodel_update(period_data)
    session.add(period)
    session.commit()
    session.refresh(period)
    return period


def delete_period(session: Session, period: models.Period) -> None:
    session.delete(period)
    session.commit()


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
    if order == "desc":  # pragma: no branch
        statement = statement.order_by(desc(models.Period.start_date))
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def eval_cycle_metrics(session: Session, user_id: str) -> None:
    # Placeholder for future implementation
    periods = session.exec(
        select(models.Period).where(models.Period.user_id == user_id)
    ).all()
    user = session.get(models.User, user_id)
    if user:  # pragma: no branch
        user.cycle_state = evaluate_cycle_state(periods, user.cycle_state)
        session.add(user)
        session.commit()


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

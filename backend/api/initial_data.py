import logging
from datetime import UTC, datetime, timedelta

import numpy as np
from sqlmodel import Session, select

from api.db import models
from api.db.crud import user as user_crud
from api.db.models import UserCreate
from api.db.session import engine
from api.utils.config import settings
from api.utils.stats import evaluate_cycle_state, evaluate_temperature_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_temp_readings(session: Session, user: models.User) -> None:
    """
    Initialize the database with simulated temperature readings and period events.
    """
    # Seed for reproducible test data
    np.random.seed(42)
    random_temps = np.random.normal(loc=36.5, scale=0.3, size=100)
    now = datetime.now(UTC)
    # simulated cycle:
    # periods: latest ended yesterday, started 4 days ago. Previous two were a month apart
    # elevated phase started 14 days before each period start
    test_periods = [
        {
            "start_date": now - timedelta(days=64),
            "end_date": now - timedelta(days=61),
        },
        {
            "start_date": now - timedelta(days=34),
            "end_date": now - timedelta(days=31),
        },
        {
            "start_date": now - timedelta(days=4),
            "end_date": now - timedelta(days=1),
        },
    ]
    temp_set_1 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1],
        }
        for day in range(78, 94)
    ]
    ele_set_1 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1] + 0.7,
        }
        for day in range(65, 77)
    ]
    temp_set_2 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1],
        }
        for day in range(48, 64)
    ]
    ele_set_2 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1] + 0.7,
        }
        for day in range(35, 47)
    ]
    temp_set_3 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1],
        }
        for day in range(18, 34)
    ]
    ele_set_3 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1] + 0.7,
        }
        for day in range(5, 17)
    ]
    temp_set_4 = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1],
        }
        for day in range(0, 4)
    ]
    test_temperatures = (
        temp_set_1
        + ele_set_1
        + temp_set_2
        + ele_set_2
        + temp_set_3
        + ele_set_3
        + temp_set_4
    )
    db_periods: list[models.Period] = []
    for period in test_periods:
        new_period = models.CreatePeriod(
            user_id=user.user_id,
            start_date=period["start_date"],
            end_date=period["end_date"],
            duration=(period["end_date"] - period["start_date"]).days,
        )
        db_period = models.Period.model_validate(new_period)
        session.add(db_period)
        db_periods.append(db_period)
    for temp in test_temperatures:
        new_temp = models.CreateTempRead(
            user_id=user.user_id,
            timestamp=temp["timestamp"],
            temperature=round(temp["temperature"], 1),
        )
        db_temp = models.Temperature.model_validate(new_temp)
        session.add(db_temp)
    session.commit()
    session.refresh(user)
    # Update user's temperature state
    user_temps = session.exec(
        select(models.Temperature).where(models.Temperature.user_id == user.user_id)
    ).all()
    user.temp_state = evaluate_temperature_state(user_temps, user.temp_state)
    user.cycle_state = evaluate_cycle_state(db_periods, user.cycle_state)
    session.add(user)
    session.commit()


def init_user(session: Session) -> None:
    if not user_crud.get_user_by_username(session=session, username=settings.FIRST_USER):
        user_in = UserCreate(
            username=settings.FIRST_USER, password=settings.FIRST_USER_PASS, is_admin=True
        )
        user = user_crud.create_user(session=session, user=user_in)
        create_temp_readings(session=session, user=user)


def init() -> None:
    with Session(engine) as session:
        init_user(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

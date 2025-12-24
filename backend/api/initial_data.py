import logging
from datetime import UTC, datetime, timedelta

import numpy as np
from sqlmodel import Session, select

from api.db import models
from api.db.crud import user as user_crud
from api.db.models import UserCreate
from api.db.session import engine
from api.utils.config import settings
from api.utils.stats import evaluate_temperature_state

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_temp_readings(
    session: Session,
    user: models.User,
    with_elevated_phase: bool = True,
) -> None:
    """
    Create temperature readings for a user for testing purposes.

    Args:
        session: Database session
        user: User to create readings for
        with_elevated_phase: If True, adds high readings to trigger elevated phase
    """
    # Seed for reproducible test data
    np.random.seed(42)
    random_temps = np.random.normal(loc=36.5, scale=0.3, size=30)
    now = datetime.now(UTC)
    # Make test temps for the last 30 days
    test_temperatures = [
        {
            "timestamp": now - timedelta(days=day),
            "temperature": random_temps[day - 1],
        }
        for day in range(3, 30)
    ]
    for temp in test_temperatures:
        new_temp = models.CreateTempRead(
            user_id=user.user_id,
            timestamp=temp["timestamp"],
            temperature=round(temp["temperature"], 1),
        )
        db_temp = models.Temperature.model_validate(new_temp)
        session.add(db_temp)
    if with_elevated_phase:
        # Make additional high readings so the next high
        # reading triggers an elevated phase
        for x in range(3):
            new_temp = models.CreateTempRead(
                user_id=user.user_id,
                timestamp=now - timedelta(days=x),
                temperature=37.5,
            )
            db_temp = models.Temperature.model_validate(new_temp)
            session.add(db_temp)
    session.commit()
    # Update user's temperature state
    user_temps = session.exec(
        select(models.Temperature).where(models.Temperature.user_id == user.user_id)
    ).all()
    user.temp_state = evaluate_temperature_state(user_temps)
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

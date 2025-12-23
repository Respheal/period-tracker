from datetime import UTC, datetime, timedelta

import numpy as np
from sqlmodel import Session, select

from api.db import models
from api.utils.stats import evaluate_temperature_state

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


# TODO: this is all rough draft stuff. Clean up before merging into main
def create_temp_readings(session: Session, user: models.User) -> None:
    for temp in test_temperatures:
        new_temp = models.CreateTempRead(
            user_id=user.user_id,
            timestamp=temp["timestamp"],
            temperature=round(temp["temperature"], 1),
        )
        db_temp = models.Temperature.model_validate(new_temp)
        session.add(db_temp)
    # Make two additional high readings from yesterday and the day before so the next
    # reading either triggers a "high phase" or not depending on today's value
    extra_highs = [
        {
            "timestamp": now - timedelta(days=1),
            "temperature": 37.5,
        },
        {
            "timestamp": now - timedelta(days=2),
            "temperature": 37.5,
        },
    ]
    for high_temp in extra_highs:
        new_temp = models.CreateTempRead(
            user_id=user.user_id,
            timestamp=high_temp["timestamp"],
            temperature=high_temp["temperature"],
        )
        db_temp = models.Temperature.model_validate(new_temp)
        session.add(db_temp)
    user_temps = session.exec(
        select(models.Temperature).where(models.Temperature.user_id == user.user_id)
    ).all()
    user.temp_state = evaluate_temperature_state(user_temps)
    session.add(user)
    session.commit()

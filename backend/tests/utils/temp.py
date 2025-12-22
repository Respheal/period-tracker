from datetime import UTC, datetime, timedelta

import numpy as np
from sqlmodel import Session

from api.db import models

random_temps = np.random.normal(loc=36.5, scale=0.3, size=30)
now = datetime.now(UTC)
# Make test temps for the last 30 days
test_temperatures = [
    {
        "timestamp": str(now - timedelta(days=day)),
        "temperature": random_temps[day - 1],
    }
    for day in range(3, 30)
]


def create_temp_readings(session: Session, user: models.User) -> None:
    for temp in test_temperatures:
        new_temp = models.CreateTempRead(
            user_id=user.user_id,
            timestamp=temp["timestamp"],
            temperature=temp["temperature"],
        )
        db_temp = models.Temperature(**new_temp.model_dump())
        session.add(db_temp)
    # Make two additional high readings from yesterday and the day before so the next
    # reading either triggers a "high phase" or not depending on today's value
    extra_highs = [
        {
            "timestamp": str(now - timedelta(days=1)),
            "temperature": 37.5,
        },
        {
            "timestamp": str(now - timedelta(days=2)),
            "temperature": 37.5,
        },
    ]
    for temp in extra_highs:
        new_temp = models.CreateTempRead(
            user_id=user.user_id,
            timestamp=temp["timestamp"],
            temperature=temp["temperature"],
        )
        db_temp = models.Temperature(**new_temp.model_dump())
        session.add(db_temp)

    session.commit()

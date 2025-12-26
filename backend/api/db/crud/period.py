from sqlmodel import Session

from api.db import models


def create_period_event(session: Session, period: models.CreatePeriod) -> models.Period:
    db_period = models.Period.model_validate(period)
    session.add(db_period)
    session.commit()
    session.refresh(db_period)
    return db_period

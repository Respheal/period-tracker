from datetime import UTC, datetime
from typing import Sequence

from sqlmodel import Session, desc, select

from api.db import models


def create_symptom_event(
    session: Session, symptom: models.CreateSymptomEvent
) -> models.SymptomEvent:
    db_symptoms = models.SymptomEvent.model_validate(symptom)
    session.add(db_symptoms)
    session.commit()
    session.refresh(db_symptoms)
    return db_symptoms


def get_event(
    session: Session,
    symptom_id: int,
    user_id: str | None = None,
) -> models.SymptomEvent | None:
    if user_id is None:  # pragma: no cover
        return session.get(models.SymptomEvent, symptom_id)
    return session.exec(
        select(models.SymptomEvent).where(
            models.SymptomEvent.pid == symptom_id,
            models.SymptomEvent.user_id == user_id,
        )
    ).first()


def get_symptom_events(
    session: Session,
    user_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    order: str = "desc",
    offset: int = 0,
    limit: int = 100,
) -> Sequence[models.SymptomEvent]:
    # By default, return the most recent 100 readings
    statement = select(models.SymptomEvent)
    if user_id:
        statement = statement.where(models.SymptomEvent.user_id == user_id)
    if start_date:
        statement = statement.where(models.SymptomEvent.date >= start_date)
    if end_date:
        statement = statement.where(models.SymptomEvent.date <= end_date)
    if order == "desc":
        statement = statement.order_by(desc(models.SymptomEvent.date))
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def update_symptom_event(
    session: Session, symptom: models.SymptomEvent, data: models.UpdateSymptomEvent
) -> models.SymptomEvent:
    symptom_data = data.model_dump(exclude_unset=True)
    if (
        "date" in symptom_data
        and symptom_data["date"] is not None
        and isinstance(symptom_data["date"], str)
    ):
        symptom_data["date"] = datetime.strptime(
            symptom_data["date"], "%Y-%m-%d"
        ).replace(tzinfo=UTC)
    symptom.sqlmodel_update(symptom_data)
    session.add(symptom)
    session.commit()
    session.refresh(symptom)
    return symptom


def delete_symptom_event(session: Session, symptom: models.SymptomEvent) -> None:
    session.delete(symptom)
    session.commit()

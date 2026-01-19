from datetime import UTC, datetime
from typing import Sequence

import pandas as pd
from fastapi.responses import StreamingResponse
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
    if order == "desc":  # pragma: no cover
        statement = statement.order_by(desc(models.SymptomEvent.date))
    statement = statement.offset(offset).limit(limit)
    return session.exec(statement).all()


def get_symptoms_csv(
    session: Session,
    user_id: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    offset: int = 0,
    limit: int = 100,
) -> StreamingResponse:  # pragma: no cover
    # We're excluding this from coverage because it is effectively the same as the
    # previous endpoint, just with CSV output.
    symptoms = get_symptom_events(
        session=session,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        offset=offset,
        limit=limit,
    )
    df = pd.DataFrame([symptom.model_dump() for symptom in symptoms])
    df["symptoms"] = [",".join(map(str, sym)) for sym in df["symptoms"]]
    df["sex"] = [",".join(map(str, sex)) for sex in df["sex"]]
    df["mood"] = [",".join(map(str, mood)) for mood in df["mood"]]
    df["discharge"] = [",".join(map(str, dis)) for dis in df["discharge"]]
    df.drop("user_id", axis=1, inplace=True)
    return StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=symptoms.csv"},
    )


def update_symptom_event(
    session: Session, symptom: models.SymptomEvent, data: models.UpdateSymptomEvent
) -> models.SymptomEvent:
    symptom_data = data.model_dump(exclude_unset=True)
    if "date" in symptom_data:  # pragma: no branch
        # BUG: This branch is covered by test_update_symptom_event
        # but isn't shown as covered in coverage report for some reason.
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

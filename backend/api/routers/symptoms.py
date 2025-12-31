from datetime import UTC, datetime
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from api.db import models
from api.db.crud import symptoms as symptom_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_admin_user, get_current_user
from api.utils.dependencies import CommonEventParams, get_session

router = APIRouter(
    prefix="/symptoms",
    tags=["symptoms"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_symptom_event(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    params: models.CreateSymptomParams,
    session: Annotated[Session, Depends(get_session)],
) -> models.SymptomEvent:
    if not params.date:
        params.date = datetime.now(UTC).isoformat()
    symptom = models.CreateSymptomEvent(
        user_id=current_user.user_id,
        date=params.date,
        flow_intensity=params.flow_intensity,
        symptoms=params.symptoms,
        mood=params.mood,
        ovulation_test=params.ovulation_test,
        discharge=params.discharge,
        sex=params.sex,
    )
    db_symptom = symptom_crud.create_symptom_event(session, symptom)
    return db_symptom


@router.get("/", dependencies=[Depends(get_admin_user)])
async def get_symptom_events(
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.Response:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    symptoms = symptom_crud.get_symptom_events(
        session=session,
        user_id=None,
        start_date=start_datetime,
        end_date=end_datetime,
        order="desc",
        offset=params.offset,
        limit=params.limit,
    )
    return models.Response(events={"symptoms": symptoms}, count=len(symptoms))


@router.get("/me/", dependencies=[Depends(get_current_user)])
async def get_my_symptom_events(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.Response:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    symptoms = symptom_crud.get_symptom_events(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        order="desc",
        offset=params.offset,
        limit=params.limit,
    )
    return models.Response(events={"symptoms": symptoms}, count=len(symptoms))


@router.get("/me/{symptom_id}")
async def get_single_symptom_event(
    symptom_id: int,
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.SymptomEvent:
    symptom_event = symptom_crud.get_event(
        session=session,
        symptom_id=symptom_id,
        user_id=current_user.user_id,
    )
    if not symptom_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom event not found",
        )
    return symptom_event


@router.patch("/me/{symptom_id}")
async def update_symptom_event(
    symptom_id: int,
    update_data: models.UpdateSymptomEvent,
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.SymptomEvent:
    symptom_event = symptom_crud.get_event(
        session=session,
        symptom_id=symptom_id,
        user_id=current_user.user_id,
    )
    if not symptom_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom event not found",
        )
    updated_symptom = symptom_crud.update_symptom_event(
        session=session,
        symptom=symptom_event,
        data=update_data,
    )
    return updated_symptom


@router.delete("/me/{symptom_id}")
async def delete_symptom_event(
    symptom_id: int,
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.ResourceDeleteResponse:
    symptom_event = symptom_crud.get_event(
        session=session,
        symptom_id=symptom_id,
        user_id=current_user.user_id,
    )
    if not symptom_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom event not found",
        )
    symptom_crud.delete_symptom_event(
        session=session,
        symptom=symptom_event,
    )
    return models.ResourceDeleteResponse(
        resource_type="symptom", resource_id=str(symptom_id)
    )


@router.get("/me/csv/", dependencies=[Depends(get_current_user)])
async def export_symptoms_csv(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> StreamingResponse:  # pragma: no cover
    # We're excluding this from coverage because it is effectively the same as the
    # previous endpoint, just with CSV output.
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    symptoms = symptom_crud.get_symptom_events(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        order="desc",
        offset=params.offset,
        limit=params.limit,
    )
    df = pd.DataFrame([symptom.model_dump() for symptom in symptoms])
    df["symptoms"] = [",".join(map(str, sym)) for sym in df["symptoms"]]
    df["sex"] = [",".join(map(str, sex)) for sex in df["sex"]]
    df["mood"] = [",".join(map(str, mood)) for mood in df["mood"]]
    df["discharge"] = [",".join(map(str, dis)) for dis in df["discharge"]]
    df.drop("user_id", axis=1, inplace=True)
    stream = StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=symptoms.csv"},
    )
    return stream

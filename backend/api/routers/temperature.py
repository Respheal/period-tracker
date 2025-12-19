from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from api.db import models
from api.db.crud import temperature as temp_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_admin_user, get_current_user
from api.utils.dependencies import CommonEventParams, get_session
from api.utils.stats import get_temp_averages

router = APIRouter(
    prefix="/temp",
    tags=["temperature"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_temp_reading(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    temperature: Annotated[
        float, Body(embed=True, ge=30, le=40, description="Temperature in Celsius")
    ],
    session: Annotated[Session, Depends(get_session)],
) -> models.Temperature:
    return temp_crud.create_temp_reading(
        session=session,
        reading=models.CreateTempRead(
            user_id=current_user.user_id, temperature=temperature
        ),
    )


@router.get("/", dependencies=[Depends(get_admin_user)])
async def get_temp_readings(
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.EventResponse:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    readings = temp_crud.get_temp_readings(
        session=session,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    return models.EventResponse(events=readings, count=readings.__len__())


@router.get("/me/", dependencies=[Depends(get_current_user)])
async def get_my_readings(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.EventResponse:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    readings = temp_crud.get_temp_readings(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    return models.EventResponse(events=readings, count=readings.__len__())


@router.get("/me/averages/", dependencies=[Depends(get_current_user)])
async def get_my_temp_averages(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.EventResponse:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    readings = temp_crud.get_temp_readings(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        order="asc",
        offset=params.offset,
        limit=params.limit,
    )
    return models.EventResponse(
        events=get_temp_averages(readings), count=readings.__len__()
    )


@router.get("/me/csv/", dependencies=[Depends(get_current_user)])
async def get_my_temp_readings_csv(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> StreamingResponse:  # pragma: no cover
    # We're excluding this from coverage because it is effectively the same as the
    # previous endpoint, just with CSV output.
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    readings = temp_crud.get_temp_readings(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        order="asc",
        offset=params.offset,
        limit=params.limit,
    )
    with_averages = get_temp_averages(readings)
    df = pd.DataFrame([avg.model_dump() for avg in with_averages])
    df["timestamp"] = df["timestamp"].dt.date
    df["average_temperature"] = df["average_temperature"].round(2)
    stream = StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=temperature_readings.csv"},
    )
    return stream

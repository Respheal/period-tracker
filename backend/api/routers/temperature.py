import json
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from api.db import models
from api.db.crud import temperature as temp_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_admin_user, get_current_user
from api.utils.dependencies import CommonEventParams, get_session
from api.utils.stats import (
    compute_baseline,
    compute_smoothed_temperature,
    temperatures_to_frame,
)

router = APIRouter(
    prefix="/temp",
    tags=["temperature"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_temp_reading(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    params: models.CreateTempParams,
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
) -> models.Temperature:
    new_temp = temp_crud.create_temp_reading(
        session=session,
        reading=models.CreateTempRead(
            user_id=current_user.user_id, temperature=params.temperature
        ),
    )
    background_tasks.add_task(
        temp_crud.update_temperature_state, session, current_user.user_id
    )
    return new_temp


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
    precision: Annotated[int, Query(embed=True, description="Decimal precision")] = 2,
) -> list[models.TemperatureEMA]:
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
    df = temperatures_to_frame(readings)
    df.insert(1, "ewm", compute_smoothed_temperature(df))
    df.insert(2, "baseline", compute_baseline(df))
    df.reset_index(inplace=True)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["ewm"] = df["ewm"].round(precision)
    df["baseline"] = df["baseline"].round(precision)
    data: list[models.TemperatureEMA] = json.loads(
        df.to_json(
            orient="records",
            double_precision=precision,
        )
    )
    return data


@router.get("/me/csv/", dependencies=[Depends(get_current_user)])
async def get_my_temp_readings_csv(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
    precision: Annotated[int, Query(embed=True, description="Decimal precision")] = 2,
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
    df = temperatures_to_frame(readings)
    df.insert(1, "ewm", compute_smoothed_temperature(df))
    df.insert(2, "baseline", compute_baseline(df))
    df.reset_index(inplace=True)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d")
    df["ewm"] = df["ewm"].round(precision)
    df["baseline"] = df["baseline"].round(precision)
    stream = StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=temperature_readings.csv"},
    )
    return stream

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from api.db import models
from api.db.crud import period as period_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_admin_user, get_current_user
from api.utils.dependencies import CommonEventParams, get_session
from api.utils.stats import periods_to_frame, predict_next_period

router = APIRouter(
    prefix="/period",
    tags=["period"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_period_event(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    params: models.CreatePeriodParams,
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
) -> models.Period:
    start_date, end_date = convert_dates_to_range(params.start_date, params.end_date)
    period = models.CreatePeriod(
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
        duration=(end_date - start_date).days if end_date and start_date else None,
    )
    db_period = period_crud.create_period_event(session, period)
    # If we have consistent temperature data, update the length of the luteal phase with
    # this period as the end of the phase
    if current_user.temp_state and current_user.temp_state.phase in [
        models.TempPhase.LOW,
        models.TempPhase.ELEVATED,
    ]:
        background_tasks.add_task(period_crud.update_luteal_length, session, db_period)
    return db_period


@router.get("/", dependencies=[Depends(get_admin_user)])
async def get_all_periods(
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.EventResponse:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    periods = period_crud.get_periods(
        session=session,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    return models.EventResponse(events=periods, count=periods.__len__())


@router.get("/me/", dependencies=[Depends(get_current_user)])
async def get_my_periods(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> models.EventResponse:
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    periods = period_crud.get_periods(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    return models.EventResponse(events=periods, count=periods.__len__())


@router.get("/me/{period_id}")
async def get_single_period(
    period_id: int,
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.Period:
    period = period_crud.get_single_period(
        session=session,
        period_id=period_id,
        user_id=current_user.user_id,
    )
    if period is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Period not found."
        )
    return period


@router.patch("/me/{period_id}")
async def update_period(
    period_id: int,
    period_update: models.PeriodUpdate,
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    background_tasks: BackgroundTasks,
) -> models.Period:
    period = period_crud.get_single_period(
        session=session,
        period_id=period_id,
        user_id=current_user.user_id,
    )
    if period is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Period not found."
        )
    period = period_crud.update_period(session=session, period=period, data=period_update)
    # Update luteal length after updating the period if necessary
    if (
        period_update.start_date is not None
        and current_user.temp_state
        and current_user.temp_state.phase
        in [models.TempPhase.LOW, models.TempPhase.ELEVATED]
    ):
        background_tasks.add_task(period_crud.update_luteal_length, session, period)
    return period


@router.delete("/me/{period_id}")
async def delete_period(
    period_id: int,
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.ResourceDeleteResponse:
    period = period_crud.get_single_period(
        session=session, period_id=period_id, user_id=current_user.user_id
    )
    if period is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Period not found."
        )
    period_crud.delete_period(session=session, period=period)
    return models.ResourceDeleteResponse(
        resource_type="period", resource_id=str(period_id)
    )


@router.get("/me/csv/", dependencies=[Depends(get_current_user)])
async def get_my_periods_csv(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonEventParams, Depends()],
) -> StreamingResponse:  # pragma: no cover
    # We're excluding this from coverage because it is effectively the same as the
    # previous endpoint, just with CSV output.
    start_datetime, end_datetime = convert_dates_to_range(
        params.start_date, params.end_date
    )
    periods = period_crud.get_periods(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    df = periods_to_frame(periods)
    df["start"] = df["start"].dt.strftime("%Y-%m-%d")
    df["end"] = df["end"].dt.strftime("%Y-%m-%d")
    df["luteal_length"] = df["luteal_length"].round(0)
    stream = StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=periods.csv"},
    )
    return stream


@router.get("/me/next")
async def get_next_period(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.Period | None:
    if current_user.cycle_state is None:
        return None
    periods = period_crud.get_periods(
        session=session, user_id=current_user.user_id, limit=6, order="desc"
    )
    if periods is None:
        return None
    return predict_next_period(cycle_state=current_user.cycle_state, periods=periods)

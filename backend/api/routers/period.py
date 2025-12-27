from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlmodel import Session

from api.db import models
from api.db.crud import period as period_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_current_user
from api.utils.dependencies import get_session
from api.utils.stats import predict_next_period

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


@router.get("/next")
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

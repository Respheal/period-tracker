from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.db import models
from api.db.crud import period as period_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_current_user
from api.utils.dependencies import get_session

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
) -> models.Period:
    start_date, end_date = convert_dates_to_range(params.start_date, params.end_date)
    period = models.CreatePeriod(
        user_id=current_user.user_id,
        start_date=start_date,
        end_date=end_date,
        duration=(end_date - start_date).days if end_date and start_date else None,
    )
    db_period = period_crud.create_period_event(session, period)
    return db_period

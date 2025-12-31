from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from api.db import models
from api.db.crud import period as period_crud
from api.db.crud import symptoms as symptom_crud
from api.db.crud import temperature as temp_crud
from api.db.crud import user as user_crud
from api.utils import convert_dates_to_range
from api.utils.auth import get_admin_user, get_current_user
from api.utils.dependencies import CommonEventParams, CommonUserParams, get_session
from api.utils.stats import combine_events

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_user(
    user: models.UserCreate,
    session: Annotated[Session, Depends(get_session)],
) -> models.UserSafe:
    if user_crud.get_user_by_username(session, user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username must be unique."
        )
    return user_crud.create_user(session=session, user=user)


@router.get("/", dependencies=[Depends(get_admin_user)])
async def get_users(
    session: Annotated[Session, Depends(get_session)],
    params: Annotated[CommonUserParams, Depends()],
) -> models.Response:
    """
    Endpoint to retrieve users for admin moderation. Admin-only.

    :return: A list of safe user representations (sans sensitive info)
    :rtype: Sequence[UserSafe]
    """
    users = user_crud.get_users(session=session, offset=params.offset, limit=params.limit)
    return models.Response(events={"users": users}, count=len(users))


@router.get("/me/")
async def read_me(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
) -> models.UserProfile:
    return current_user


@router.patch("/me/")
async def update_me(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    user_update: models.UserUpdate,
) -> models.UserProfile:
    user = session.get(models.User, current_user.user_id)
    # If the user doesn't exist, we'll hit an auth error before we get here,
    # so type ignore
    return user_crud.update_user(session, user, user_update)  # type: ignore


@router.delete("/me/")
async def delete_me(
    current_user: Annotated[models.UserProfile, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.ResourceDeleteResponse:
    user_crud.delete_user(session=session, user_id=current_user.user_id)
    return models.ResourceDeleteResponse(
        resource_type="user", resource_id=current_user.user_id
    )


@router.get("/me/events/")
async def get_my_events(
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
        offset=params.offset,
        limit=params.limit,
    )
    temperatures = temp_crud.get_temp_readings(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    periods = period_crud.get_periods(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    return models.Response(
        count=len(symptoms) + len(temperatures) + len(periods),
        events={"periods": periods, "symptoms": symptoms, "temperatures": temperatures},
    )


@router.get("/me/events/csv/")
async def get_my_events_csv(
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
        offset=params.offset,
        limit=params.limit,
    )
    temperatures = temp_crud.get_temp_readings(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    periods = period_crud.get_periods(
        session=session,
        user_id=current_user.user_id,
        start_date=start_datetime,
        end_date=end_datetime,
        offset=params.offset,
        limit=params.limit,
    )
    df = combine_events(symptoms=symptoms, temperatures=temperatures, periods=periods)
    stream = StreamingResponse(
        iter([df.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=events.csv"},
    )
    return stream

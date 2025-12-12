from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from api.db import models
from api.db.crud import user as user_crud
from api.utils.auth import get_current_user
from api.utils.dependencies import get_session

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


@router.post("/")
async def create_user(
    user: models.UserCreate,
    session: Annotated[Session, Depends(get_session)],
) -> models.UserStats:
    if user_crud.get_user_by_username(session, user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username must be unique."
        )
    return user_crud.create_user(session=session, user=user)


@router.get("/me/")
async def read_me(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.UserStats:
    return current_user


@router.patch("/me/")
async def update_me(
    current_user: Annotated[models.User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    user_update: models.UserUpdate,
) -> models.UserStats:
    db_user = user_crud.get_user_by_id(session, current_user.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user_crud.update_user(session, db_user, user_update)


@router.delete("/me/")
async def delete_me(
    current_user: Annotated[models.User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
) -> models.ResourceDeleteResponse:
    user_crud.delete_user(session=session, user_id=current_user.user_id)
    return models.ResourceDeleteResponse(
        resource_type="user", resource_id=current_user.user_id
    )


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> list[dict[str, str]]:
    return [{"item_id": "Foo", "owner": current_user.username}]

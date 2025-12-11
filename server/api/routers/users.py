from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from api.db.crud import user as user_crud
from api.db.models.user import User
from api.utils.dependencies import get_session

router = APIRouter(tags=["users"])


@router.get("/users/")
async def read_users(
    session: Annotated[Session, Depends(get_session)],
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    return user_crud.get_users(session, offset=offset, limit=limit)


@router.post("/users/")
async def create_user(
    name: str,
    session: Annotated[Session, Depends(get_session)],
) -> User:
    return user_crud.create_user(User(name=name), session)

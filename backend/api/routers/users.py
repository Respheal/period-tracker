from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from api.db.models import User, UserBase
from api.utils.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


# @router.get("/users/", dependencies=[Depends(oauth2_scheme)])
# async def read_users(
#     session: Annotated[Session, Depends(get_session)],
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 100,
# ) -> list[User]:
#     return user_crud.get_users(session, offset=offset, limit=limit)

# @router.post("/users/")
# async def create_user(
#     name: str,
#     session: Annotated[Session, Depends(get_session)],
# ) -> User:
#     return user_crud.create_user(User(name=name), session)


@router.get("/me/")
async def read_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserBase:
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict[str, str]]:
    return [{"item_id": "Foo", "owner": current_user.username}]

from sqlmodel import Session

from api.db import models
from api.db.crud import user as user_crud
from tests.utils import random_lower_string

TEST_USERS = {
    # Primary user for "current user" tests
    "jim": {
        "display_name": "Jim Hawkins",
        "is_admin": False,
        "is_disabled": False,
    },
    "sarah": {
        "display_name": "Sarah Connor",
        "is_admin": False,
        "is_disabled": False,
    },
    "coco": {
        "display_name": None,
        "is_admin": False,
        "is_disabled": True,
    },
}


def create_random_user(
    session: Session,
    username: str | None = None,
    password: str | None = None,
    display_name: str | None = None,
    is_admin: bool = False,
    is_disabled: bool = False,
) -> models.User:
    user_in = models.UserCreate(
        username=username or random_lower_string(),
        password=password or random_lower_string(),
        display_name=display_name,
        is_admin=is_admin,
        is_disabled=is_disabled,
    )
    return user_crud.create_user(session=session, user=user_in)


def create_test_users(session: Session) -> None:
    for username, user_data in TEST_USERS.items():
        create_random_user(
            session=session,
            username=username,
            display_name=user_data["display_name"],
            is_admin=user_data["is_admin"],
            is_disabled=user_data["is_disabled"],
        )

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from api.db.crud import user as user_crud
from api.utils.config import settings
from tests.utils import random_lower_string
from tests.utils.user import TEST_USERS


def get_admin_headers(client: TestClient) -> dict[str, str]:
    r = client.post(
        "/auth/",
        data={
            "username": settings.FIRST_USER,
            "password": settings.FIRST_USER_PASS,
        },
    )
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


def get_user_headers(client: TestClient, db: Session, username: str) -> dict[str, str]:
    password = random_lower_string()
    user = user_crud.get_user_by_username(session=db, username=username)
    if not user:
        if username in TEST_USERS:
            user_data = TEST_USERS[username]
            user_in_create = models.UserCreate(
                username=username,
                password=password,
                display_name=user_data["display_name"],
                is_admin=user_data["is_admin"],
                is_disabled=user_data["is_disabled"],
            )
        else:
            user_in_create = models.UserCreate(username=username, password=password)
        user = user_crud.create_user(session=db, user=user_in_create)
    else:
        user = user_crud.update_user(
            session=db, user=user, data=models.UserUpdate(password=password)
        )
    r = client.post("/auth/", data={"username": username, "password": password})
    response = r.json()
    return {"Authorization": f"Bearer {response["access_token"]}"}

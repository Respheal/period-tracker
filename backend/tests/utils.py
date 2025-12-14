import random
import string

from fastapi.testclient import TestClient
from sqlmodel import Session

from api.db import models
from api.db.crud import user as user_crud
from api.utils.config import Settings


def settings() -> Settings:
    return Settings()


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def create_random_user(db: Session) -> models.User:
    user_in = models.UserCreate(
        username=random_lower_string(),
        password=random_lower_string(),
    )
    return user_crud.create_user(session=db, user_create=user_in)


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
        user_in_create = models.UserCreate(username=username, password=password)
        user = user_crud.create_user(session=db, user=user_in_create)
    else:
        user = user_crud.update_user(
            session=db, user=user, data=models.UserUpdate(password=password)
        )
    r = client.post("/auth/", data={"username": username, "password": password})
    response = r.json()
    return {"Authorization": f"Bearer {response["access_token"]}"}

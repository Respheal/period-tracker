from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session

from api.db import models
from api.utils import auth
from api.utils.config import Settings
from api.utils.dependencies import get_session, get_settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


@router.post("/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.Token:
    user = auth.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return models.Token(
        access_token=auth.create_token(
            user_id=user.user_id, token_type="access", settings=settings
        ),
        refresh_token=auth.create_token(
            user_id=user.user_id, token_type="refresh", settings=settings
        ),
        token_type="bearer",  # nosec B106
    )


@router.post("/refresh")
async def refresh_token(
    refresh_token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.Token:
    return await auth.refresh_access_token(refresh_token=refresh_token, settings=settings)

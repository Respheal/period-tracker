from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
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


@router.post("/")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.LoginResponse:
    user = auth.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    refresh_token = auth.create_token(user=user, token_type="refresh", settings=settings)
    return models.LoginResponse(
        access_token=auth.create_token(
            user=user, token_type="access", settings=settings
        ),  # nosec B106
        refresh_token=refresh_token,
        token_type="bearer",  # nosec B106
    )


@router.post("/refresh")
async def refresh_tokens(
    token: models.RefreshToken,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.LoginResponse:
    return await auth.refresh_tokens(
        refresh_token=token.refresh_token, session=session, settings=settings
    )

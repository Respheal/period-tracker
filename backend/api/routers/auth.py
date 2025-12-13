from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/", refreshUrl="auth/refresh/")


def set_refresh_cookie(
    response: Response,
    refresh_token: str,
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.post("/")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.AccessToken:
    user = auth.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Bandit can't figure out the nosec on this call, so it's a generic nosec
    set_refresh_cookie(
        response,
        auth.create_token(user=user, token_type="refresh", settings=settings),  # nosec
        settings,
    )
    return models.AccessToken(
        access_token=auth.create_token(
            user=user, token_type="access", settings=settings
        ),  # nosec B106
        token_type="bearer",  # nosec B106
    )


@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.AccessToken:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = await auth.refresh_tokens(
        refresh_token=refresh_token, session=session, settings=settings
    )
    set_refresh_cookie(response, tokens["refresh_token"], settings)
    return models.AccessToken(
        access_token=tokens["access_token"],
        token_type="bearer",  # nosec B106
    )

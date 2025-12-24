from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session

from api.db import models
from api.db.crud import user as user_crud
from api.utils.config import Settings
from api.utils.dependencies import get_session, get_settings
from api.utils.redis_client import get_redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/")
password_hash = PasswordHash.recommended()
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed version."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash the given password."""
    return password_hash.hash(password)


def authenticate_user(
    session: Annotated[Session, Depends(get_session)], username: str, password: str
) -> models.User | None:
    """Authenticate user by username and password."""
    user = user_crud.get_user_by_username(session=session, username=username)
    if user and not user.is_disabled and verify_password(password, user.hashed_password):
        return user
    return None


def create_token(
    user: models.User,
    token_type: Literal["access", "refresh"],
    settings: Settings,
    refreshed: bool = False,
) -> str:
    """
    Create a JWT token with 'sub' matching the user_id.

    Args:
        user_id (str): The ID of the user.
        token_type (Literal["access", "refresh"]): The type of token to create.
        settings (Settings): App settings containing secret key and token lifetimes.
    Returns:
        str: The encoded JWT token.
    """
    now = datetime.now(timezone.utc)
    if token_type == "access":  # nosec B105
        exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    elif token_type == "refresh":  # nosec B105
        exp = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    else:
        raise ValueError("Invalid token type")
    to_encode = {
        "token_type": token_type,
        "jti": str(uuid4()),
        "sub": user.user_id,
        "iat": now,
        "exp": now + exp,
        "user": {"is_disabled": user.is_disabled, "is_admin": user.is_admin},
        "refreshed": refreshed,
    }

    # Use RSA private key for RS256, or SECRET_KEY for HS256
    signing_key = (
        settings.get_private_key()
        if settings.ALGORITHM == "RS256"
        else settings.SECRET_KEY
    )
    return jwt.encode(to_encode, key=signing_key, algorithm=settings.ALGORITHM)


def validate_token(
    token: str,
    token_type: Literal["access", "refresh"],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.TokenPayload:
    """
    Validate a JWT token and return its payload.

    Args:
        token (str): The JWT token to validate.
        token_type (Literal["access", "refresh"]): The expected type of the token.
        settings (Settings): App settings containing secret key and algorithm.
    Returns:
        models.TokenPayload: The decoded token payload.
    """
    try:
        # Use RSA public key for RS256, or SECRET_KEY for HS256
        verification_key = (
            settings.get_public_key()
            if settings.ALGORITHM == "RS256"
            else settings.SECRET_KEY
        )
        payload = models.TokenPayload.model_validate(
            jwt.decode(token, verification_key, algorithms=[settings.ALGORITHM])
        )
        if payload.sub is None or payload.token_type != token_type:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return payload


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.User:
    """Get the current user based on the provided JWT token payload."""
    payload: models.TokenPayload = validate_token(
        token=token, token_type="access", settings=settings  # nosec B106
    )
    user = session.get(models.User, payload.sub)
    if user is None or user.is_disabled:
        raise credentials_exception
    return user


async def get_admin_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models.User:
    """Verify if the current user is an admin."""
    user = await get_current_user(token=token, session=session, settings=settings)
    if user.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return user


async def refresh_tokens(
    refresh_token: str,
    session: Annotated[Session, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    """Refresh access and refresh tokens using a valid refresh token."""
    payload: models.TokenPayload = validate_token(
        token=refresh_token, token_type="refresh", settings=settings  # nosec B106
    )
    user = session.get(models.User, payload.sub)
    # Check if user is disabled or token is revoked
    redis_client = get_redis_client()
    if user is None or user.is_disabled or redis_client.get(f"{payload.jti}"):
        raise credentials_exception
    # Disable the used refresh token
    redis_client.set(f"{payload.jti}", 1, ex=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    return {
        "access_token": create_token(
            user=user,
            token_type="access",  # nosec B106
            settings=settings,
            refreshed=True,
        ),
        "refresh_token": create_token(
            user=user, token_type="refresh", settings=settings
        ),  # nosec B106
    }

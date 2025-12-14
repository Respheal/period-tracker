from datetime import datetime
from typing import Literal
from uuid import uuid4

from sqlmodel import Field, SQLModel

###
# Utility Models
###


class ApplicationInfo(SQLModel):
    app_name: str
    version: str


class HealthCheck(SQLModel):
    status: str
    timestamp: datetime


class ResourceDeleteResponse(SQLModel):
    resource_type: str
    resource_id: str


###
# Token
###
class Token(SQLModel):
    token_type: str


class AccessToken(Token):
    access_token: str


class RefreshToken(Token):
    refresh_token: str


class TokenPayload(SQLModel):
    token_type: Literal["access", "refresh"]
    jti: str
    sub: str
    iat: datetime
    exp: datetime
    user: "UserState"
    refreshed: bool = False  # require login to access secure resources if true


###
# User
###
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    display_name: str | None = None


class UserState(SQLModel):
    is_disabled: bool = Field(default=False)
    is_admin: bool = Field(default=False)


class UserCreate(UserBase, UserState):
    # username
    # display_name
    # is_disabled
    # is_admin
    password: str


class UserSafe(UserBase, UserState):
    """
    Everything but the hashed password and period stats.
    - user_id
    - username
    - display_name
    - is_disabled
    - is_admin

    """

    # username
    # display_name
    # is_disabled
    # is_admin
    user_id: str = Field(
        default_factory=lambda: str(uuid4()), primary_key=True, index=True
    )


class UserProfile(UserSafe):
    """
    Everything but the hashed password.
    - user_id
    - username
    - display_name
    - is_disabled
    - is_admin

    """

    # username
    # display_name
    # is_disabled
    # is_admin
    # user_id
    average_cycle_length: float | None = None
    average_period_length: float | None = None


class User(UserProfile, table=True):
    """
    User model.

    This is the class representing the User table in the database.
    This should never be part of a serialized response. User UserSafe or UserProfile
    for that purpose.

    - user_id
    - username
    - display_name
    - is_disabled
    - is_admin
    - average_cycle_length
    - average_period_length
    - hashed_password

    """

    # username
    # display_name
    # is_disabled
    # is_admin
    # user_id
    # average_cycle_length
    # average_period_length

    hashed_password: str


class UserUpdate(SQLModel):
    display_name: str | None = None
    password: str | None = None
    average_cycle_length: float | None = None
    average_period_length: float | None = None
    is_disabled: bool | None = None
    is_admin: bool | None = None


###
# Metadata
###

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = SQLModel.metadata
metadata.naming_convention = NAMING_CONVENTION
target_metadata = [metadata, User.metadata, Token.metadata]

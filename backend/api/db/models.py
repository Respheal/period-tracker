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
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(SQLModel):
    token_type: Literal["access", "refresh"]
    jti: str
    sub: str
    iat: datetime
    exp: datetime


###
# User
###
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    display_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserStats(UserBase):
    user_id: str = Field(
        default_factory=lambda: str(uuid4()), primary_key=True, index=True
    )
    average_cycle_length: float | None = None
    average_period_length: float | None = None


class User(UserStats, table=True):
    # username, display_name inherited from UserBase
    # user_id, average_cycle_length, average_period_length inherited from UserStats
    hashed_password: str
    disabled: bool = False


class UserUpdate(SQLModel):
    display_name: str | None = None
    password: str | None = None
    average_cycle_length: float | None = None
    average_period_length: float | None = None
    disabled: bool | None = None


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

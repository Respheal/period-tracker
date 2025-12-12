from datetime import datetime
from typing import Literal
from uuid import uuid4

from sqlmodel import Field, SQLModel


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


class User(UserBase, table=True):
    user_id: str = Field(
        default_factory=lambda: str(uuid4()), primary_key=True, index=True
    )
    hashed_password: str
    disabled: bool = False


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

import enum
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from sqlalchemy import DateTime
from sqlmodel import JSON, Column, Enum, Field, Relationship, SQLModel

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


class Response(SQLModel):
    """Base response model with count field used for list endpoints."""

    count: int


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
class UserResponse(Response):
    # count
    users: list[UserSafe]


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
    temp_state: TemperatureState | None = None


class User(UserSafe, table=True):
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
    - hashed_password

    """

    # username
    # display_name
    # is_disabled
    # is_admin
    # user_id
    temp_state: TemperatureState = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={"uselist": False},
    )
    hashed_password: str


class UserUpdate(SQLModel):
    display_name: str | None = None
    password: str | None = None


class UserAdminUpdate(UserUpdate):
    is_disabled: bool | None = None
    is_admin: bool | None = None


###
# Events
###


class EventBase(SQLModel):
    user_id: str = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")


class CreateTempRead(EventBase):
    # user_id
    temperature: float  # Celsius
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), index=True),
    )


class Temperature(CreateTempRead, table=True):
    """
    Temperature Event model.

    This is the class representing the Temperature table in the database.

    - user_id
    - temperature
    - pid
    - timestamp
    """

    # user_id
    # temperature
    pid: int | None = Field(default=None, primary_key=True, index=True)


class TempPhase(str, enum.Enum):
    LEARNING = "learning"
    LOW = "low_phase"
    ELEVATED = "elevated_phase"
    UNKNOWN = "unknown"


class TemperatureState(SQLModel, table=True):
    pid: int | None = Field(default=None, primary_key=True, index=True)
    user_id: str = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")
    phase: TempPhase = Field(default=TempPhase.LEARNING)
    baseline: float | None = None
    last_evaluated: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    user: User = Relationship(back_populates="temp_state")


class CreatePeriod(EventBase):
    # user_id
    start_date: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    end_date: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    duration: int | None = None  # in days


class Period(CreatePeriod, table=True):
    """
    Period Event model.

    This is the class representing the Period table in the database.

    - user_id
    - start_date
    - end_date
    - duration
    """

    # user_id
    # start_date
    # end_date
    # duration
    id: int = Field(default=None, primary_key=True, index=True)


class FlowIntensity(str, enum.Enum):
    NONE = "none"
    SPOTTING = "spotting"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class CreateSymptomEvent(EventBase):
    # user_id
    date: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    flow_intensity: FlowIntensity | None = Field(
        sa_column=Column(Enum(FlowIntensity), nullable=True)
    )
    symptoms: list[str] | None = Field(sa_column=Column(JSON), unique_items=True)
    mood: list[str] | None = Field(sa_column=Column(JSON), unique_items=True)
    ovulation_test: bool | None = None
    discharge: list[str] | None = Field(sa_column=Column(JSON), unique_items=True)
    sex: list[str] | None = Field(sa_column=Column(JSON), unique_items=True)


class SymptomEvent(CreateSymptomEvent, table=True):
    """
    Symptom Event model.

    This is the class representing the Symptom Event table in the database.
    - user_id
    - date
    - flow_intensity
    - symptoms
    - mood
    - ovulation_test
    - discharge
    - sex
    """

    # user_id
    # date
    # flow_intensity
    # symptoms
    # mood
    # ovulation_test
    # discharge
    # sex
    id: int = Field(default=None, primary_key=True, index=True)


class EventResponse(Response):
    # count
    events: list[Temperature | Period | SymptomEvent]


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

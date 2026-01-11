import enum
from datetime import UTC, date, datetime, timedelta
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import Body
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
    events: dict[str, list[Temperature | Period | SymptomEvent | UserSafe]]


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
    user: UserState
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
    temp_state: TemperatureState | None = None
    cycle_state: Cycle | None = None


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
    cycle_state: Cycle = Relationship(
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


# Temperature


class CreateTempParams(SQLModel):
    temperature: float = Field(ge=30.0, le=40.0)  # Celsius


class CreateTempRead(EventBase, CreateTempParams):
    # user_id
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )


class Temperature(CreateTempRead, table=True):
    """
    Temperature Event model.

    This is the class representing the Temperature table in the database.

    - user_id
    - temperature
    - pid
    - timestamp, assume TZ-naive on read due to SQLite limitations
    """

    # user_id
    # temperature
    timestamp: datetime = Field(sa_column=Column(DateTime(), index=True))
    pid: int | None = Field(default=None, primary_key=True, index=True)


class TempUpdate(SQLModel):
    temperature: Annotated[float | None, Body(default=None, ge=30.0, le=40.0)] = None
    timestamp: Annotated[
        str | None,
        Body(
            default=None,
            description="YYYY-MM-DD format",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = None


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
    last_evaluated: datetime | None = Field(default=None, sa_column=Column(DateTime()))
    user: User = Relationship(back_populates="temp_state")


class TemperatureEMA(SQLModel):
    timestamp: str
    temperature: float
    ewm: float
    baseline: float


# Period


class CreatePeriodParams(SQLModel):
    start_date: Annotated[
        str,
        Body(
            default=str((datetime.now(UTC) - timedelta(days=3)).date().isoformat()),
            description="Start date",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ]
    end_date: Annotated[
        str | None,
        Body(
            default=str(datetime.now(UTC).date().isoformat()),
            description="End date (Optional)",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = str(datetime.now(UTC).date().isoformat())


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
    - start_date, assume TZ-naive on read due to SQLite limitations
    - end_date, assume TZ-naive on read due to SQLite limitations
    - duration
    """

    # user_id
    # duration
    start_date: datetime = Field(sa_column=Column(DateTime()))
    end_date: datetime | None = Field(
        default=None, sa_column=Column(DateTime(), nullable=True)
    )
    pid: int = Field(default=None, primary_key=True, index=True)
    luteal_length: int | None = None  # in days


class PredictedPeriod(SQLModel):
    start_date: date
    end_date: date
    confidence: float | None = None


class PeriodUpdate(SQLModel):
    start_date: Annotated[
        str | None,
        Body(
            default=None, description="YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"
        ),
    ] = None
    end_date: Annotated[
        str | None,
        Body(
            default=None, description="YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$"
        ),
    ] = None


class PeriodMetrics(SQLModel):
    start: str
    end: str | None = None
    luteal_length: int | None = None


class CycleState(str, enum.Enum):
    LEARNING = "learning"
    STABLE = "stable"
    UNSTABLE = "unstable"


class Cycle(SQLModel, table=True):
    pid: int | None = Field(default=None, primary_key=True, index=True)
    user_id: str = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")
    state: CycleState = Field(default=CycleState.LEARNING)
    avg_cycle_length: int | None = None
    avg_period_length: int | None = None
    last_period_start: datetime | None = None
    last_evaluated: datetime | None = Field(default=None, sa_column=Column(DateTime()))
    user: User = Relationship(back_populates="cycle_state")


class FlowIntensity(str, enum.Enum):
    NONE = 0
    SPOTTING = 1
    LIGHT = 2
    MEDIUM = 3
    HEAVY = 4


class CreateSymptomParams(SQLModel):
    date: Annotated[
        str | None,
        Body(
            default=str((datetime.now(UTC) - timedelta(days=1)).date().isoformat()),
            description="Date of the symptom event",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = None
    flow_intensity: FlowIntensity | None = None
    symptoms: list[str] | None = None
    mood: list[str] | None = None
    ovulation_test: bool | None = None
    discharge: list[str] | None = None
    sex: list[str] | None = None


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


class UpdateSymptomEvent(SQLModel):
    date: Annotated[
        str | None,
        Body(
            default=None,
            description="YYYY-MM-DD format",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = None
    flow_intensity: FlowIntensity | None = None
    symptoms: list[str] | None = None
    mood: list[str] | None = None
    ovulation_test: bool | None = None
    discharge: list[str] | None = None
    sex: list[str] | None = None


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
    date: datetime = Field(sa_column=Column(DateTime(), index=True))
    pid: int = Field(default=None, primary_key=True, index=True)


class SymptomSummary(SQLModel):
    flow_intensity: FlowIntensity = FlowIntensity.NONE
    symptoms: set[str] = set()
    mood: set[str] = set()
    ovulation_test: bool = False
    discharge: set[str] = set()
    sex: set[str] = set()


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
target_metadata = [metadata]

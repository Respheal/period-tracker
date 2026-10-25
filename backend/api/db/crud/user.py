from datetime import UTC, datetime
from typing import Sequence

from sqlmodel import Session, select

from api.db.models import (
    TemperatureState,
    User,
    UserCreate,
    UserCycle,
    UserProfile,
    UserTemperatureState,
    UserUpdate,
)
from api.utils import auth


def get_users(session: Session, offset: int = 0, limit: int = 100) -> Sequence[User]:
    """
    Retrieve a list of users for the purposes of user moderation by an admin.
    """
    return session.exec(select(User).offset(offset).limit(limit)).all()


def get_user(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)


def create_user(session: Session, user: UserCreate) -> User:
    db_user = User.model_validate(
        user, update={"hashed_password": auth.get_password_hash(user.password)}
    )
    session.add(db_user)
    session.flush()
    # Initialize temp and cycle state
    now = datetime.now(UTC)
    init_temp_state = UserTemperatureState(user_id=db_user.user_id, last_evaluated=now)
    init_cycle_state = UserCycle(user_id=db_user.user_id, last_evaluated=now)
    session.add(init_temp_state)
    session.add(init_cycle_state)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).one_or_none()


def update_user(session: Session, user: User, data: UserUpdate) -> User:
    user_data = data.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        extra_data["hashed_password"] = auth.get_password_hash(user_data["password"])
    user.sqlmodel_update(user_data, update=extra_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: str) -> None:
    session.delete(get_user(session, user_id))
    session.commit()


def update_temp_state(
    session: Session, user_id: str, new_state: TemperatureState
) -> User | None:
    user = get_user(session, user_id)
    if not user:  # pragma: no cover
        return None
    user.temp_state.sqlmodel_update(new_state.model_dump(exclude_unset=True))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def add_partner(session: Session, user: User, partner: User) -> User:
    if partner not in user.partners:
        user.partners.append(partner)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def remove_partner(session: Session, user: User, partner: User) -> User:
    if partner in user.partners:
        user.partners.remove(partner)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def is_partner(session: Session, user: UserProfile, partner_id: str) -> bool:
    partner = get_user(session, partner_id)
    if not partner:
        return False
    return partner in (user.partners or [])

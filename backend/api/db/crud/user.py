from typing import Sequence

from sqlmodel import Session, select

from api.db.models import TemperatureState, User, UserCreate, UserUpdate
from api.utils import auth
from api.utils.stats import evaluate_cycle_state, evaluate_temperature_state


def get_users(session: Session, offset: int = 0, limit: int = 100) -> Sequence[User]:
    """
    Retrieve a list of users for the purposes of user moderation by an admin.
    """
    return session.exec(select(User).offset(offset).limit(limit)).all()


def create_user(session: Session, user: UserCreate) -> User:
    db_user = User.model_validate(
        user, update={"hashed_password": auth.get_password_hash(user.password)}
    )
    session.add(db_user)
    # Initialize temp state
    db_user.temp_state = evaluate_temperature_state([])
    # Initialize cycle state
    db_user.cycle_state = evaluate_cycle_state([])
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
    user = session.get(User, user_id)
    session.delete(user)
    session.commit()


def update_temp_state(
    session: Session, user_id: str, new_state: TemperatureState
) -> User | None:
    user = session.get(User, user_id)
    if not user:  # pragma: no cover
        return None
    user.temp_state = new_state
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

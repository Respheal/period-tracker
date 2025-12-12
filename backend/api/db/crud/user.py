from sqlmodel import Session, select

from api.db.models import User, UserCreate, UserUpdate
from api.utils import auth


def create_user(session: Session, user: UserCreate) -> User:
    db_user = User(
        username=user.username,
        display_name=user.display_name,
        hashed_password=auth.get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_id(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).one_or_none()


def update_user(session: Session, user: User, data: UserUpdate) -> User:
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.password is not None:
        user.hashed_password = auth.get_password_hash(data.password)
    if data.average_cycle_length is not None:
        user.average_cycle_length = data.average_cycle_length
    if data.average_period_length is not None:
        user.average_period_length = data.average_period_length
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: str) -> None:
    user = get_user_by_id(session, user_id)
    if user:
        session.delete(user)
        session.commit()

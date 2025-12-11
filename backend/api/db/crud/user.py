from sqlmodel import Session, select

from api.db.models import User, UserCreate
from api.utils import auth


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).one_or_none()


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

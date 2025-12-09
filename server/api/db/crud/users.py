from sqlmodel import Session, select

from api.db.models import User


def get_users(session: Session, offset: int = 0, limit: int = 100) -> list[User]:
    return list(session.exec(select(User).offset(offset).limit(limit)).all())


def create_user(user: User, session: Session) -> User:
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

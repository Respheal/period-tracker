import logging

from sqlmodel import Session

from api.db.crud import user as user_crud
from api.db.models import UserCreate
from api.db.session import engine
from api.utils.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_user(session: Session) -> None:
    if not user_crud.get_user_by_username(session=session, username=settings.FIRST_USER):
        user_in = UserCreate(
            username=settings.FIRST_USER, password=settings.FIRST_USER_PASS, is_admin=True
        )
        user_crud.create_user(session=session, user=user_in)


def init() -> None:
    with Session(engine) as session:
        init_user(session)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()

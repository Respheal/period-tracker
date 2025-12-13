import os

from sqlmodel import create_engine

from api.utils.config import settings

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///./{settings.DATABASE}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)

import os
from pathlib import Path

import sqlalchemy.exc as exc
from dotenv import load_dotenv
from sqlmodel import create_engine

from api.utils.config import settings

if os.environ.get("ENVIRONMENT") == "test":
    # Alembic has no dotenv support, so we need to load the test env file manually
    env_path = rf"{Path(__file__).absolute().parent.parent.parent.parent}/.env.test"
    load_dotenv(env_path, override=True)

DATABASE_HOST = os.environ.get("DATABASE", settings.DATABASE)
DATABASE_URL = f"sqlite:///./{DATABASE_HOST}"

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )
except exc.ArgumentError:
    print("Error creating engine:", DATABASE_URL)
    raise

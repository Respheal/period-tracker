import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import create_engine

from api.utils.config import settings

if os.environ.get("ENVIRONMENT") == "test":  # pragma: no branch
    # Alembic has no dotenv support, so we need to load the test env file manually
    # Pytest otherwise behaves and reads from .env.test automatically
    env_path = rf"{Path(__file__).absolute().parent.parent.parent.parent}/.env.test"
    load_dotenv(env_path, override=True)

DATABASE_DIR = os.environ.get("DATA_DIR", "./data/")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_FILE = os.environ.get("DATABASE", settings.DATABASE)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}{DATABASE_FILE}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False},
)

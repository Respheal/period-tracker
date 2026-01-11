# period-tracker

[![codecov](https://codecov.io/github/Respheal/period-tracker/branch/main/graph/badge.svg?token=VFMH4T7LRL)](https://codecov.io/github/Respheal/period-tracker)

The blood moon rises once again.

This project is a WIP for an open-source period tracker, made by and for people who menstruate, have a Docker box, and don't like phone apps.

So far the project is exclusively a backend, but a frontend is on the [todo list](./notes/TODO.md).

## Requirements

- Python 3.14
- Poetry (or pip to install poetry from [requirements.txt](./backend/requirements.txt))

## To Run (Locally)

Copy `.env.sample` to `.env` and update the values for your personal use. Most analysis variables can be finetuned as needed through the environmental variable configuration.

```bash
cd backend
pip install -r requirements.txt
poetry install
# Set up the database with the admin user defined in env
./scripts/prestart.sh
# Run the app
poetry run uvicorn api.main:app --reload
```

## To Run (Docker)

> [!WARNING]
> Persistent volumes have not been configured yet. Data will be lost if the container is deleted.

Copy `.env.sample` to `.env` and update the values for your personal use. Most analysis variables can be finetuned as needed through the environmental variable configuration.

```bash
docker compose up -d --build
```

The backend app will be available on port 5000.

## Development

### Application Structure

- **`api/routers/`** - API endpoints
- **`api/db/models.py`** - SQLModel ORM models
- **`api/db/crud/`** - CRUD functionality
- **`api/utils/`** - Shared utilities
- **`api/utils/config.py`** - Base configuration (overwritten by .env)
- **`api/utils/stats.py`** - Cycle analysis and processing

### Database Models and Migrations

To update the database structure, update the models in **`api/db/models.py`**. After updates, you can generate an alembic migration to make use of the new model.

```bash
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
```

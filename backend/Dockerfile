FROM python:3.14-slim-bookworm AS builder

COPY ./requirements.txt ./
RUN pip install -r requirements.txt
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /poetry

COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --only main --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.14-slim-bookworm AS runtime

ENV VIRTUAL_ENV=/poetry/.venv \
    PATH="/poetry/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./scripts /scripts
# nuke windows line endings
RUN sed -i 's/\r$//g' /scripts/prestart.sh
RUN chmod -R +x /scripts

COPY ./alembic.ini /alembic.ini
COPY ./alembic /alembic
COPY ./api ./api
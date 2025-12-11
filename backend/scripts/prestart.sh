#! /usr/bin/env bash

set -e
set -x

export PYTHONPATH="$(dirname "$(dirname "$(readlink -f "$0")")")"

# Let the DB start
python ./api/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python ./api/initial_data.py

unset PYTHONPATH
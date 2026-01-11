#! /usr/bin/env bash

set -e
set -x

export PYTHONPATH="$(dirname "$(dirname "$(readlink -f "$0")")")"

# Check for the presence of public and private keys
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
KEYS_DIR="$SCRIPT_DIR/../keys"

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo "Warning: openssl is not installed. Cannot generate RSA keys."
    echo "Please install openssl and generate RSA keys, or update your .env to use ALGORITHM=HS256."
    echo "To generate keys:"
    echo "  openssl genrsa -out $KEYS_DIR/private_key.pem 2048"
    echo "  openssl rsa -in $KEYS_DIR/private_key.pem -out $KEYS_DIR/public_key.pem -pubout"
    echo "Continuing without key generation..."
else
    # Create keys directory if it doesn't exist
    mkdir -p "$KEYS_DIR"

    if [ ! -f "$KEYS_DIR/private.pem" ]; then
        echo "Generating private key..."
        openssl genrsa -out "$KEYS_DIR/private.pem" 2048
    fi

    if [ ! -f "$KEYS_DIR/public.pem" ]; then
        echo "Generating public key..."
        openssl rsa -in "$KEYS_DIR/private.pem" -out "$KEYS_DIR/public.pem" -pubout
    fi

    echo "Keys found successfully"
fi

# Let the DB start
python ./api/backend_pre_start.py

# Run migrations
alembic upgrade head

# Create initial data in DB
python ./api/initial_data.py

unset PYTHONPATH
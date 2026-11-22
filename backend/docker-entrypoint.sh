#!/bin/sh
# Backend entrypoint: run migrations and seed before starting the server
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding database..."
python app/seed.py

echo "Starting backend server..."
exec "$@"

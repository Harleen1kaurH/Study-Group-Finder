#!/bin/sh
# entrypoint.sh -- runs on every container start.
#
# Applies any pending Alembic migrations first, then starts the API server.
# Running migrations here (rather than as a separate manual step) means a
# fresh App Runner deploy always brings the database schema up to date
# automatically, matching whatever code is in the image.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

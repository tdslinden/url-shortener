#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete!"

echo "Starting Gunicorn..."
exec gunicorn app:app \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    --access-logfile - \
    --error-logfile - \
    --log-level info

#!/bin/sh
set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Run seed script
if [ -f "app/seed.py" ]; then
    echo "Seeding database..."
    python app/seed.py 2>/dev/null || true
fi

# Execute the main command
exec "$@"

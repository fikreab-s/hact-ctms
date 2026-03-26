#!/bin/bash
# =============================================================================
# HACT CTMS — Django Entrypoint Script
# Waits for PostgreSQL, runs migrations, collects static, starts server
# =============================================================================
set -e

echo "============================================="
echo "  HACT CTMS — Starting Django Application"
echo "============================================="

# Wait for PostgreSQL to be ready
echo "[1/4] Waiting for PostgreSQL..."
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

until python -c "
import socket, sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect(('${POSTGRES_HOST}', ${POSTGRES_PORT}))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    echo "  PostgreSQL not ready — retrying in 2s..."
    sleep 2
done
echo "  PostgreSQL is ready!"

# Only run migrations/collectstatic for the main Django API (not Celery workers)
if echo "$@" | grep -q "gunicorn"; then
    # Generate migrations for HACT apps (development only)
    echo "[2/5] Generating migrations..."
    python manage.py makemigrations accounts clinical ops safety lab outputs audit --noinput

    # Run database migrations
    echo "[3/5] Running database migrations..."
    python manage.py migrate --noinput

    # Collect static files
    echo "[3/4] Collecting static files..."
    python manage.py collectstatic --noinput

    # Create superuser if DJANGO_SUPERUSER_* env vars are set
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
        echo "[3.5/4] Creating superuser..."
        python manage.py createsuperuser --noinput 2>/dev/null || echo "  Superuser already exists."
    fi
else
    echo "[2/4] Skipping migrations (not gunicorn process)."
    echo "[3/4] Skipping collectstatic (not gunicorn process)."
fi

echo "[4/4] Starting application server..."
echo "============================================="

# Execute the CMD passed to the container (gunicorn or other)
exec "$@"

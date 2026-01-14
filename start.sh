#!/bin/bash

# Exit on error
set -e

echo "Starting deployment setup..."

# 1. Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# 2. Import default photo rules (if table is empty)
echo "Importing default photo rules..."
python manage.py import_rules

# 3. Create a superuser if it doesn't exist (optional but helpful)
# You can set DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL in Koyeb
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || true
fi

# 4. Start Gunicorn
echo "Starting Gunicorn..."
# Use the WEB_CONCURRENCY env var if set, otherwise default to 1 for memory safety on Nano
exec gunicorn validphoto.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${WEB_CONCURRENCY:-1} \
    --timeout 300 \
    --log-level debug

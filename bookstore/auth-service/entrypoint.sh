#!/bin/bash
set -e
echo "==> Creating migrations..."
python manage.py makemigrations --noinput
echo "==> Running migrations..."
python manage.py migrate --noinput
echo "==> Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile - --error-logfile -

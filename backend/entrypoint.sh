#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "$SEED_DATA" = "true" ]; then
  python manage.py shell -c "from bounty.models import WantedCriminal; import sys; sys.exit(0 if WantedCriminal.objects.exists() else 1)" \
    || python manage.py loaddata seed
fi


if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" 2>/dev/null \
    || echo "Superuser already exists"
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:${APP_PORT:-8000} --workers 3 --access-logfile -
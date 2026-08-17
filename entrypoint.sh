#!/bin/sh

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

PORT=${PORT:-8011}

mkdir -p /app/logs

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "$(echo $DJANGO_DEV | tr '[:upper:]' '[:lower:]')" = "true" ]; then
  exec python manage.py runserver 0.0.0.0:$PORT
else
  exec gunicorn medihub.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile  /app/logs/gunicorn_error.log \
    --capture-output \
    --log-level info
fi

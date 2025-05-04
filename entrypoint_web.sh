#!/bin/bash

# Ожидаем, пока база будет доступна
echo "Waiting for postgres..."

while ! nc -z $DB_HOST 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Create staticfiles directory with proper permissions
mkdir -p /app/staticfiles
chmod -R 777 /app/staticfiles

# Применяем миграции
python manage.py migrate

# Собираем статику
python manage.py collectstatic --noinput

# Запускаем Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000

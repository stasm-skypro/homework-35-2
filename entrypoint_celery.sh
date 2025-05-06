#!/bin/bash

# Ожидаем, пока база будет доступна
echo "Waiting for postgres..."

while ! nc -z $DB_HOST 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Применяем миграции
python manage.py migrate

# Создаём директории логов и файлы логов
mkdir -p /app/materials/logs && mkdir -p /app/users/logs
touch /app/materials/logs/reports.log && touch /app/users/logs/reports.log

# Запускаем Celery
celery -A config worker --loglevel=info

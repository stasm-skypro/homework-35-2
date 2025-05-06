#!/bin/bash

# Ожидаем, пока база будет доступна
echo "Waiting for postgres..."

while ! nc -z $DB_HOST 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

# Применяем миграции
python manage.py migrate

# Создаём директории логов и файлы логов (запускаем скрипт)
source "$(dirname "$0")/entrypoint_prepare_logs.sh"

# Запускаем Celery-beat
celery -A config beat --loglevel=info

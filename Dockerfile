# Используем Python-образ
FROM python:3.12-slim

# Создаем группу и пользователя
RUN groupadd -r groupdjango && useradd -r -g groupdjango userdj

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Установим netcat для ожидания сервисов
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Копируем все файлы проекта в контейнер
COPY . .

# Копируем скрипт и даём права
COPY entrypoint_web.sh /entrypoint_web.sh
COPY entrypoint_celery.sh /entrypoint_celery.sh
COPY entrypoint_celery_beat.sh /entrypoint_celery_beat.sh
RUN chmod +x /entrypoint_web.sh
RUN chmod +x /entrypoint_celery.sh
RUN chmod +x /entrypoint_celery_beat.sh

# Меняем пользователя на userdj
USER userdj

# Указываем команду по умолчанию (для web)
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

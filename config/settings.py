"""
Django settings for config project.
"""

import os
import sys
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения из .env file
load_dotenv(override=True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", False) == "True"

hosts = os.getenv("DJANGO_ALLOWED_HOSTS")
ALLOWED_HOSTS = hosts.split(",") if hosts else []

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
# Third-party apps
INSTALLED_APPS += [
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_yasg",
    "corsheaders",
    "django_celery_beat",
]
# Local apps
INSTALLED_APPS += ["users", "materials"]  # User model  # Material model

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
MIDDLEWARE += [
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Almaty"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024  # max 2 MB

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "users.User"

# Настройка аутентификации (необходимо для того, чтобы пользователь после успешной регистрации автоматически
# входил в систему)
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Настройка логгера
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(asctime)s - %(name)s - %(levelname)s: %(message)s"},
    },
    "handlers": {
        "users_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "users/logs/reports.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
            "delay": True,  # <-- отложенное открытие файла: файл будет открыт только при первом логе,
            # а не сразу при конфигурации
        },
        "materials_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "materials/logs/reports.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
            "delay": True,  # <-- отложенное открытие файла: файл будет открыт только при первом логе,
            # а не сразу при конфигурации
        },
    },
    "loggers": {
        "users": {
            "handlers": ["users_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "materials": {
            "handlers": ["materials_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "courses": {
            "handlers": ["materials_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Настройка DjangoFilterBackend
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [  # Настройка фильтрации данных
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [  # Настройка аутентификации
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": (  # Настройка прав доступа для всех контроллеров
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# Настройка Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),  # Настройка времени жизни токена доступа
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),  # Настройка времени жизни токена обновления
    "AUTH_HEADER_TYPES": ("Bearer",),  # Настройка типа заголовка для токена
}

# Настройка Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")

# Настройка Cors
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

# Настройка Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")  # URL-адрес брокера сообщений
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")  # URL-адрес брокера результатов, также Redis
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"

# Настройка почты
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT", 587)
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

# Настройка лёгкой БД для тестов
if "test" in sys.argv:
    DATABASES["default"] = {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}

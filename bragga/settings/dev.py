from bragga.settings.base import *
from decouple import config
import os

DEBUG = True

SECRET_KEY = config('SECRET_KEY', default='dev-secret-key')

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="bragga_dev_db"),
        "USER": config("POSTGRES_USER", default="postgres"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
        "OPTIONS": {
            "connect_timeout": 10,
        }
    }
}

# Em desenvolvimento, usar filesystem storage para simplificar
if os.getenv('USE_S3_STORAGE') != 'true':
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Email em desenvolvimento - console backend
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Email produção - SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configurações de debug
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Cache em desenvolvimento
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Configurações de sessão
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Configurações de segurança para desenvolvimento
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
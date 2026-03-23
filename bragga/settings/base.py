from pathlib import Path
from decouple import config
import os
from colorlog import ColoredFormatter

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------------------------------------------------------------------------------
# APLICAÇÕES
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    
    'user.apps.UserConfig',


    # Terceiros
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django_extensions',
    'storages',
    'widget_tweaks',
    'django_filters',
    'phonenumber_field',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'bragga.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            
            ],
        },
    },
]

WSGI_APPLICATION = 'bragga.wsgi.application'
SITE_ID = 1

#AUTH_USER_MODEL = 'user.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ------------------------------------------------------------------------------
# ARQUIVOS ESTÁTICOS E MÍDIA
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID", default="minio")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY", default="minio123")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME", default="media")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL", default="http://minio:9000")
MINIO_ACCESS_URL = config("MINIO_ACCESS_URL", default="http://localhost:9000")

MEDIA_URL = f"{MINIO_ACCESS_URL}/{AWS_STORAGE_BUCKET_NAME}/"

STORAGES = {
    "default": {"BACKEND": "user.storage.S3MediaStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# ------------------------------------------------------------------------------
# AUTENTICAÇÃO / ALLAUTH
# ------------------------------------------------------------------------------

AUTH_USER_MODEL = 'user.User'

ACCOUNT_RATE_LIMITS = {
    "signup": "10/h",
    "login": "5/m",
    "reset_password_email": "5/h",
    "confirm_email": "10/h",
}

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 10
ACCOUNT_EMAIL_SUBJECT_PREFIX = 'Bragga Dev'
ACCOUNT_EMAIL_CONFIRMATION_HMAC = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
ACCOUNT_EMAIL_MAX_LENGTH = 100
ACCOUNT_MAX_EMAIL_ADDRESSES = 1
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
LOGIN_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_PASSWORD_INPUT_RENDER_VALUE = False
ACCOUNT_PRESERVE_USERNAME_CASING = True
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username']
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
ACCOUNT_LOGIN_BY_CODE_REQUIRED = False
ACCOUNT_LOGIN_TOKEN_ENABLED = False
ACCOUNT_LOGIN_BY_CODE_ENABLED = False

# ------------------------------------------------------------------------------
# E-MAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER
ADMINS = [('Administrador', 'bragawebdevelopment@gmail.com')]
EMAIL_TIMEOUT = 30



# ------------------------------------------------------------------------------
# OUTRAS CONFIGURAÇÕES
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024 

# ------------------------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s %(message)s',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'colored'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'), 'propagate': False},
        'user.views.shared.add_address': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'boto3': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'botocore': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'storages': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}



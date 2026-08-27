from pathlib import Path
from decouple import config
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',

    'rest_framework',
    'corsheaders',

    'forecasting.apps.ForecastingConfig',
    'account.apps.AccountConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'account.middleware.JWTAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# SessionMiddleware and CsrfViewMiddlware can be theoretically
# removed for this project as JWT-based authentication is used
# instead of session-based authentication, and no forms are being
# submitted that mandates CSRF protection

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'), # Should be Docker Compose service name
        'PORT': config('DB_PORT'),
        'TEST': {
            'NAME': config('TEST_DB_NAME'),
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
os.makedirs(BASE_DIR / 'static', exist_ok=True)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "account.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # This sets IsAuthenticated as the default permission class for all views
    # and can be overridden at view-level using `permission_classes` attribute
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 4,
    "PAGE_SIZE_QUERY_PARAM": "page_size",
    "MAX_PAGE_SIZE": 8,
    # Pagination settings can be overridden at view-level using
    # `pagination_class` attribute of CBV
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Keeps Django's default loggers alive
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name} (line {lineno}): {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

PROJECT_APPS = ["account", "forecasting"]

for app_name in PROJECT_APPS:
    app_dir = BASE_DIR / app_name
    log_dir = app_dir / "logs"

    if app_dir.exists() and not log_dir.exists():
        os.makedirs(log_dir, exist_ok=True)

        handler_name = f"{app_name}_file"

        LOGGING["handlers"][handler_name] = {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_dir / f"{app_name}.log",
            "maxBytes": 1024 * 1024 * 5,  # 15 MB
            "backupCount": 3,
            "formatter": "verbose",
        }

        LOGGING["loggers"][app_name] = {
            "handlers": ["console", handler_name],
            "level": "INFO",
            "propagate": False,
        }

# Artifacts
ARTIFACTS_ROOT = BASE_DIR / "artifacts"

LOAD_MODEL = ARTIFACTS_ROOT / "load_models" / "load_xgbr_1.pkl"
GEN_MODEL = ARTIFACTS_ROOT / "gen_models" / "gen_xgbr_2.pkl"

WEATHER_MODEL = ARTIFACTS_ROOT / "london_weather_models" / "london_weather_lstm_1.keras"
WEATHER_X_SCALER = ARTIFACTS_ROOT / "london_weather_preprocessors" / "london_weather_X_scaler.pkl"
WEATHER_Y_SCALER = ARTIFACTS_ROOT / "london_weather_preprocessors" / "london_weather_y_scaler.pkl"

# Celery and Redis
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Email server configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
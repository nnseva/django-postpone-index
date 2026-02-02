"""
Django settings.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

from django2_postgres import psycopg_patch

import django


psycopg_patch.fix()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.insert(0, BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1@5n@*f2ng(+il*9im)f$ie8lpc)c3an!3-3z2f9cwn*=6pzvc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '*',
]
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'config',
    'test_unique_together',
    'test_fields',
    'test_explicit_constraint',
    'test_explicit_index',
    'test_ignore_migration',
    'postpone_index',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

if django.VERSION < (5, 1):
    INSTALLED_APPS.insert(1, 'test_index_together')

TEST_RUNNER = 'config.utils.DjangoDiscoverRunner'

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'postpone_index.contrib.postgres'),
        'NAME': os.environ.get('DATABASE_NAME', 'postpone_index'),
        'USER': os.environ.get('DATABASE_USER', 'test'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'test'),
        'HOST': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    },
    'additional': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'postpone_index.contrib.postgres'),
        'NAME': os.environ.get('DATABASE_NAME_ADDITIONAL', 'postpone_index_additional'),
        'USER': os.environ.get('DATABASE_USER', 'test'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'test'),
        'HOST': os.environ.get('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)-8s - %(name)-40s- - %(message)s [%(process)d/%(thread)d]'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'postpone_index.contrib.postgres.schema': {
            'handlers': ['console'],
            'level': os.environ.get('POSTPONE_INDEX_LOGGING', 'INFO'),
            'propagate': False,
        },
        'postpone_index': {
            'handlers': ['console'],
            'level': os.environ.get('POSTPONE_INDEX_LOGGING', 'INFO'),
            'propagate': False,
        },
        'config': {
            'handlers': ['console'],
            'level': os.environ.get('CONFIG_LOGGING', 'INFO'),
            'propagate': False,
        },
        # Again, default Django configuration to email unhandled exceptions
        'django.db': {
            'handlers': ['console'],
            'level': os.environ.get('DATABASE_LOGGING', 'INFO'),
            'propagate': False,
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'

POSTPONE_INDEX_IGNORE = os.environ.get('POSTPONE_INDEX_IGNORE', True)  # for tests
POSTPONE_INDEX_ADMIN_IGNORE = os.environ.get('POSTPONE_INDEX_ADMIN_IGNORE', False)

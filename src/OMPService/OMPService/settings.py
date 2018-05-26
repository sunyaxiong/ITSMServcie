"""
Django settings for OMPService project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'w%_kdw&9*_2filppa89j2*&&bl69je6)=$ed1nn$i9ps$@-(vg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*", ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudres',
    'gunicorn',
    'django_celery_results',
    'django_celery_beat',
    'rest_framework',
    'itsm',
    'accounts',
    'api',
    'asset',
    'lib.django_cas_ng',
    'cas_sync',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

# cas conf
SUCC_REDIRECT_URL = "itsm.ecscloud.com"
CAS_SERVER_URL = "http://cas.ecscloud.com/cas/"
# CAS_REDIRECT_URL = "http://www.baidu.com"

ROOT_URLCONF = 'OMPService.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'OMPService.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jiajie_omp',
        'USER': 'root',
        'PASSWORD': 'Admin@vstecs.com1',
        'HOST': '',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    },
    'cas_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cas',
        'USER': 'root',
        'PASSWORD': '123123Qwe',
        "HOST": "52.83.173.240",
        "PORT": "3306",
    },
}

# use multi-database in django
DATABASE_ROUTERS = ['OMPService.database_router.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    # example:
    # 'app_name':'database_name',
    'cas_sync': 'cas_db',
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/home/syx/workspace/JiajieOMP/src/OMPService/static',
]

# STATIC_ROOT = os.path.join(BASE_DIR, "static")


# Celery 4.1 conf
CELERY_BROKER_URL = 'redis://:@127.0.0.1:6379/3'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_SERIALIZER = 'json'


# REST FRAMEWORK
REST_FRAMEWORK = {
        # 'DEFAULT_AUTHENTICATION_CLASSES': (
        #     'people.authentication.CustomUserTokenAuthentication',
        #     'people.authentication.CustomUserSessionAuthentication',
        #     ),
        'DEFAULT_FILTER_BACKENDS': (
            'rest_framework.filters.DjangoFilterBackend',
            'rest_framework.filters.SearchFilter',
            'rest_framework.filters.OrderingFilter',
            ),
        'SEARCH_PARAM': 'search',
        'DEFAULT_PAGINATION_CLASS': 'lib.pagination.CommonPageNumberPagination',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
            ) if DEBUG else (
            'rest_framework.renderers.JSONRenderer',
            ),
        # 'DEFAULT_PERMISSION_CLASSES': (
        #     # 'common.permissions.ReadOnly',
        #     ),
        }

# Redis conf
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
        "TIMEOUT": 100*365*24*60*60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "KEY_PREFIX": "itsm",
        }
    }
}


# fit2cloud api conf
if DEBUG:
    CLOUD_HOST = "111.13.61.173"
    CMDB_HOST = "111.13.61.173"
    access_key = "My00ZjRkMzVkZA=="
    cloud_secret_key = "228e1f50-3b39-4213-a8d8-17e8bf2aeb1e"
    INTERNET_HOST = "111.13.61.173"
else:
    INTERNET_HOST = "cmp.ecscloud.com"
    CLOUD_HOST = "172.16.13.155"
    CMDB_HOST = "172.16.13.155"
    access_key = "My00ZjRkMzVkZA=="
    cloud_secret_key = "228e1f50-3b39-4213-a8d8-17e8bf2aeb1e"

CMDB_CONF = {
    "access_key": access_key,
    "version": "v1",
    "signature_method": "HmacSHA256",
    "signature_version": "v1"
}

CLOUD_CONF = {
    "access_key": access_key,
    "version": "v1",
    "signature_method": "HmacSHA256",
    "signature_version": "v1",
    "user": "sunyaxiong@vstecs.com",
}
secret_key = cloud_secret_key
# cloud_secret_key = '228e1f50-3b39-4213-a8d8-17e8bf2aeb1e'

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django.log',
            'formatter': 'verbose'
        },
        'email': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'email'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# mail
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'sunyaxiongnn@163.com'
EMAIL_HOST_PASSWORD = 'Sun880519'
EMAIL_SUBJECT_PREFIX = u'[vstecs.com]'
EMAIL_USE_TLS = True

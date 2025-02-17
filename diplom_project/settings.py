from pathlib import Path

import os
import rollbar
import rollbar.contrib.django.middleware as rollbar_middleware

from dotenv import load_dotenv
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-as&!070eu-#og04&%*ha53--ff3k#m&yty1va__s$cq3r!3ol_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [

    'social_django'
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'drf_spectacular',
    'cachalot',
    'baton'

    'my_app',
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
]

# Для TokenAuthentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '3/minute',  # Для неаутентифицированных пользователей
        'user': '5/minute',  # Для аутентифицированных пользователей
    }
}

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Для Google
    'social_core.backends.facebook.FacebookOAuth2',  # Для Facebook (если нужно)
    'django.contrib.auth.backends.ModelBackend',  # Стандартная авторизация
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '<YOUR_GOOGLE_CLIENT_ID>'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '<YOUR_GOOGLE_CLIENT_SECRET>'

# Facebook
SOCIAL_AUTH_FACEBOOK_KEY = '<YOUR_FACEBOOK_APP_ID>'
SOCIAL_AUTH_FACEBOOK_SECRET = '<YOUR_FACEBOOK_APP_SECRET>'

# Настройки редиректа после успешного входа
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'





MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]

ROOT_URLCONF = 'diplom_project.urls'

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

WSGI_APPLICATION = 'diplom_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('NAME_DB'),
        'HOST': '79.174.91.58',  # localhost
        'PORT': '5432',
        'USER': 'postgres',
        'PASSWORD': os.getenv('PASSWORD_DB'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
            'options': '-c search_path=diplom'
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

# Настройка для отправки электронной почты
# 'django.core.mail.backends.smtp.EmailBackend'  на почту
# 'django.core.mail.backends.console.EmailBackend'  выводит в консоль
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'  # Адрес вашего SMTP сервера
EMAIL_PORT = 465   # Порт SMTP сервера
# EMAIL_USE_TLS = True  # Использование TLS для безопасного соединения
EMAIL_USE_SSL = True  # Если вы используете SSL вместо TLS, раскомментируйте эту строку и закомментируйте EMAIL_USE_TLS
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Ваш адрес электронной почты
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Пароль от вашей почты, рекомендуется хранить в пер. окружения.

AUTH_USER_MODEL = 'my_app.CustomUser'

# Настройки celery
CELERY_TIMEZONE = 'Europe/Moscow'

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_BROKER', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BATON = {
    'SITE_NAME': 'My BOTTLE DONT TOUCH', # Персоналити-чек
    'APP_LIST': (
        'app_name',
    ),
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1', 
    }
}

ROLLBAR = {
    'access_token': 'ab6875b8ee6e42919ba7cad6c1b9d908',
    'environment': 'development' if DEBUG else 'production',
    'code_version': '1.0',
    'root': BASE_DIR,
}

rollbar.init(**ROLLBAR)
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Ler .env manualmente (simples e robusto)
env_file = BASE_DIR / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Helper para converter strings do .env
def get_env(key, default='', cast=str):
    value = os.environ.get(key, default)
    if cast == bool:
        return value.lower() in ('true', '1', 'yes')
    elif cast == list:
        return [v.strip() for v in value.split(',') if v.strip()]
    elif cast == int:
        return int(value) if value else 0
    return value

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env('SECRET_KEY', 'django-insecure-k3y#9@k_2m5p8q7r&t$w^z%a1b*c4d6e8f!g')
if SECRET_KEY.startswith('django-insecure-') and not get_env('DEBUG', 'True', bool):
    raise ValueError(
        "SECRET_KEY deve ser definida em produção. "
        "Gere uma com: python manage.py shell -c "
        '"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env('DEBUG', 'True', bool)

ALLOWED_HOSTS = get_env('ALLOWED_HOSTS', 'localhost,127.0.0.1', list)
CSRF_TRUSTED_ORIGINS = get_env('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000', list)

# Segurança de cookies (condicional por ambiente)
SESSION_COOKIE_SECURE = get_env('SESSION_COOKIE_SECURE', 'False', bool)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = get_env('CSRF_COOKIE_SECURE', 'False', bool)
CSRF_COOKIE_SAMESITE = 'Lax'

# Headers de segurança
SECURE_SSL_REDIRECT = get_env('SECURE_SSL_REDIRECT', 'False', bool)
SECURE_HSTS_SECONDS = get_env('SECURE_HSTS_SECONDS', '0', int)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cal',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'minhacarteira.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'minhacarteira.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache (desenvolvimento local)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'minhacarteira-cache',
    }
}

# Celery
CELERY_BROKER_URL = get_env('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL.replace('/0', '/1')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'

# Criptografia de campos sensíveis
from cryptography.fernet import Fernet

FERNET_SECRET_KEY = get_env('FERNET_SECRET_KEY', '')
if not FERNET_SECRET_KEY:
    # Gerar chave temporária para desenvolvimento
    FERNET_SECRET_KEY = Fernet.generate_key().decode()
    if not DEBUG:
        raise ValueError(
            "FERNET_SECRET_KEY deve ser definida em produção. "
            "Gere uma com: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
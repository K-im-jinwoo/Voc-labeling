from .base import *

import environ

ALLOWED_HOSTS = ['43.200.38.56']
STATIC_ROOT = BASE_DIR / 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
DEBUG = True

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': '5432',
    }
}
from .base import *

import environ

<<<<<<< HEAD
ALLOWED_HOSTS = ["43.200.38.56"]
STATIC_ROOT = BASE_DIR / "static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
DEBUG = False
=======
ALLOWED_HOSTS = ['43.200.38.56']
STATIC_ROOT = BASE_DIR / 'static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
DEBUG = True
>>>>>>> 8166da122754bae675d0bb8ad028cd2714ab5d02

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": "5432",
    }
}

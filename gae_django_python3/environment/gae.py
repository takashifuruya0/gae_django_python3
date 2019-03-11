from gae_django_python3.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['_DB_NAME'],
        "USER": os.environ['_DB_USER'],
        "PASSWORD": os.environ['_DB_PASSWORD'],
        'HOST': os.environ['_DB_HOST'],
        "PORT": os.environ['_DB_PORT'],
        "ATOMIC_REQUESTS": True,
    }
}

ENVIRONMENT = "gae"
DEBUG = False

GOOGLE_MAPS_API_KEY = "AIzaSyD7BCPVSpQ6Xw2li13WK0O0TCWrB_E3dLE"
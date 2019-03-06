from gae_django_python3.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "gaebase",
        "USER": 'gaeuser',
        "PASSWORD": 'Takashi&102',
        'HOST': "34.73.73.184",
        "PORT": "5432",
        "ATOMIC_REQUESTS": True,
    }
}

ENVIRONMENT = "gae"
DEBUG = False
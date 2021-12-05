import django.conf
from django.db.models import IntegerField
import sys
import pathlib

# Required for importing the server app (upper dir)
file = pathlib.Path(__file__).resolve()
root = file.parents[1]
sys.path.append(str(root))

INSTALLED_APPS = [
    'server'
]

# TODO: Put this in a separate file
cs = {
    'database': 'Game',
    'user': 'GameUser',
    'password': '123',
    'host': 'localhost',
    'port': '5432'
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': cs['database'],
        'USER': cs['user'],
        'PASSWORD': cs['password'],
        'HOST': cs['host'],
        'PORT': cs['port']
    }
}

django.conf.settings.configure(
    INSTALLED_APPS=INSTALLED_APPS,
    DATABASES=DATABASES
)

django.setup()


if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

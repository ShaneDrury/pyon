"""
Pyon settings for {{ project_name }} project.
"""
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_NAME = '{{ project_name }}'
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
DUMP_DIR = os.path.join(PROJECT_ROOT, '../results')
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = "%(levelname)s:%(name)s:%(message)s"
LOGGING_DATEFMT = None
LOGGING_FILE = None
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, '../templates'),
)
ROOT_MEASUREMENTS = '{{ project_name }}.measurements'
ROOT_PARSERS = '{{ project_name }}.parsers'

# Django things
SECRET_KEY = '{{ secret_key }}'
INSTALLED_APPS = (
    '{{ project_name }}',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

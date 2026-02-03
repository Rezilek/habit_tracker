# conftest.py
import pytest
import os
import django
from django.conf import settings

# Установите переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Настройте Django
django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Настройка тестовой базы данных."""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

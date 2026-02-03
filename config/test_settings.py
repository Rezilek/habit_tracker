from .settings import *

# Отключаем atomic requests для тестов
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Используем базу в памяти для тестов
        'ATOMIC_REQUESTS': False,
    }
}

# Отключаем пароли для тестов
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Ускоряем тесты
DEBUG = False

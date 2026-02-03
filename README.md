# Habit Tracker

Бэкенд-часть SPA веб-приложения для трекера полезных привычек.

## О проекте

Проект реализует функциональность трекера привычек на основе принципов из книги Джеймса Клира "Атомные привычки". Позволяет пользователям создавать, отслеживать и получать напоминания о полезных привычках.

## Функциональность

### Основные возможности
- Управление привычками (CRUD операции)
- JWT аутентификация пользователей
- Telegram бот для напоминаний
- Пагинация (5 привычек на страницу)
- Права доступа (только свои привычки + публичные)
- Отложенные задачи через Celery
- Документация API (Swagger/OpenAPI)

### Типы привычек
- **Полезные привычки** - действия для самосовершенствования
- **Приятные привычки** - вознаграждения за выполнение полезных
- **Связанные привычки** - связь между полезными и приятными

## Технологии

![Django](https://img.shields.io/badge/Django-4.2-green)
![DRF](https://img.shields.io/badge/DRF-3.14-blue)
![Celery](https://img.shields.io/badge/Celery-5.3-yellow)
![Redis](https://img.shields.io/badge/Redis-7.0-red)
![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)

## Установка и запуск

### Предварительные требования
- Python 3.10+
- PostgreSQL или SQLite
- Redis
- Git

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker
2. Создание виртуального окружения
bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Настройка переменных окружения
Создайте файл .env в корне проекта:

env
SECRET_KEY=your-secret-key-here
DEBUG=True
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
DB_NAME=habittracker
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
5. Настройка базы данных
bash
# Применение миграций
python manage.py makemigrations
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
6. Запуск Redis
bash
# Windows (скачайте Redis с GitHub)
redis-server.exe

# Linux
sudo systemctl start redis-server

# Mac
brew services start redis

# Или через Docker
docker run -d -p 6379:6379 --name redis redis:alpine
7. Запуск сервера
bash
# Запуск Django
python manage.py runserver

# В отдельном терминале - Celery worker
celery -A config worker --loglevel=info

# В другом терминале - Celery beat
celery -A config beat --loglevel=info
API Эндпоинты
Аутентификация
POST /users/register/ - Регистрация пользователя

POST /users/login/ - Авторизация (JWT токен)

POST /users/token/refresh/ - Обновление токена

Привычки
GET /habits/ - Список привычек пользователя (пагинация)

GET /habits/public/ - Публичные привычки

POST /habits/ - Создание привычки

GET /habits/{id}/ - Получение привычки

PUT /habits/{id}/ - Обновление привычки

DELETE /habits/{id}/ - Удаление привычки

Telegram
POST /telegram/webhook/ - Вебхук для Telegram бота

Валидаторы
Приложение включает 7 валидаторов бизнес-логики:

Нельзя одновременно указывать вознаграждение и связанную привычку

Время выполнения ≤ 120 секунд

Связанная привычка должна быть приятной

Приятная привычка не может иметь вознаграждения

Приятная привычка не может иметь связанной привычки

Нельзя выполнять привычку реже, чем 1 раз в 7 дней

Привычка не может быть связана сама с собой

Интеграция с Telegram
Создание бота
Найти @BotFather в Telegram

Команда /newbot

Указать имя бота (например, HabitTrackerBot)

Получить токен и добавить в .env

Функции бота
/start - регистрация пользователя

/help - помощь по командам

Автоматические напоминания о привычках

Подтверждение выполнения привычек

Тестирование
bash
# Запуск всех тестов
python manage.py test

# С проверкой покрытия
coverage run --omit="*/fix_*.py,*/migrations_backup_*/*,test_*.py" manage.py test
coverage report

# Создание HTML отчета
coverage html
Результаты тестирования
64 теста - все проходят

83% покрытия кода

Интеграционные тесты с Telegram

Юнит-тесты для моделей, сериализаторов, валидаторов

Тесты Celery задач

Пагинация
Все списки привычек используют пагинацию:

По умолчанию: 5 привычек на страницу

Настраиваемый параметр page_size

Поддержка запроса следующей/предыдущей страницы

Развертывание с Docker
yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: habittracker
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
Документация API
Доступна после запуска сервера:

Swagger UI: http://localhost:8000/swagger/

ReDoc: http://localhost:8000/redoc/

OpenAPI schema: http://localhost:8000/swagger.yaml

Технологический стек
Backend: Django 4.2 + Django REST Framework

База данных: PostgreSQL / SQLite

Очереди задач: Celery + Redis

Аутентификация: JWT (djangorestframework-simplejwt)

Документация: drf-yasg (Swagger/OpenAPI)

CORS: django-cors-headers

Тестирование: Django Test Framework + coverage

Линтинг: flake8

Для курсовой работы
Этот проект был разработан в рамках курсовой работы и соответствует всем требованиям:

Критерии приемки
✅ Настроен CORS

✅ Интеграция с Telegram

✅ Реализована пагинация (5 на страницу)

✅ Использованы переменные окружения

✅ Все модели описаны

✅ Все эндпоинты реализованы

✅ Настроены все валидаторы (7 шт.)

✅ Реализованы права доступа

✅ Настроены отложенные задачи через Celery

✅ Проект покрыт тестами на 83%

✅ Код соответствует best practices

✅ Имеется список зависимостей

✅ Flake8 проверка 100%

✅ Решение выложено на GitHub

Автор
Ваше Имя

Лицензия
MIT
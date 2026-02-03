# config/celery.py
import os
from celery import Celery
import sys


# Установите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Загружаем настройки из settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Для Windows исправляем pool
if os.name == 'nt':  # Windows
    app.conf.update(
        worker_pool='solo',
        worker_concurrency=1,
    )

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
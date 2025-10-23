import os
from celery import Celery
from celery.schedules import crontab

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра объекта Celery
app = Celery('lms')

# Загрузка настроек из объекта django.conf.settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из файлов tasks.py
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'check-inactive-users': {
        'task': 'lms.tasks.deactivate_inactive_users',
        # Запускать каждый день в 00:00
        'schedule': crontab(hour=0, minute=0),
    }
}

# Убедимся, что временная зона совпадает с Django
app.conf.timezone = 'UTC'

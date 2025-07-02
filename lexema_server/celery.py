import os

from celery import Celery
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lexema_server.settings")

app = Celery("lexema_server")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
# Расписание для периодических задач
app.conf.beat_schedule = {
    "check-online-users-every-30-seconds": {
        "task": "lexema_user.tasks.check_online_status",
        "schedule": timedelta(seconds=30),  # Запускать каждые 30 секунд
    },
}

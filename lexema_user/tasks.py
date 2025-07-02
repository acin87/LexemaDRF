# tasks.py
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


@shared_task
def check_online_status():

    offline_threshold = timezone.now() - timedelta(minutes=1)
    User.objects.filter(is_online=True, last_activity__lt=offline_threshold).update(
        is_online=False
    )

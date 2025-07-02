from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)


class Meta:
    db_table = "lexema_app_users"
    verbose_name = "Пользователь"
    verbose_name_plural = "Пользователи"

""" Модуль конфигурации приложения """
from django.apps import AppConfig


class LexemaAppConfig(AppConfig):
    """Конфигурация приложения"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "lexema_app"

from django.apps import AppConfig


class LexemaNotificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lexema_notification"

    def ready(self):
        import lexema_notification.signals
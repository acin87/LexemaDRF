from django.apps import AppConfig


class LexemaPostConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lexema_post"

    def ready(self):
        import lexema_post.signals

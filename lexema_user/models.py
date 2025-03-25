from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    class Meta:
        db_table = 'lexema_app_users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationType(models.TextChoices):
    FRIEND_REQUEST = 'friend_request', _('Запрос в друзья')
    FRIEND_ACCEPTED = 'friend_accepted', _('Запрос принят')
    FRIEND_REJECTED = 'friend_rejected', _('Запрос отклонён')
    FRIEND_REMOVED = 'friend_removed', _('Удалён из друзей')
    FRIEND_NEW_POST = 'friend_new_post', _('Создан новый пост')
    NEW_MESSAGE = 'new_message', _('Новое сообщение')
    TYPING_STARTED = 'typing_started', _('Печатает...')


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Получатель')
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name=_('Отправитель'),
        null=True,
        blank=True
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name=_('ТИп уведомления')
    )
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Сообщение')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Прочитано?')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Создано')
    )
    content_type = models.ForeignKey(
        'contenttypes.ContentType',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    # Для хранения дополнительных данных в JSON
    extra_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Дополнительные данные')
    )

    class Meta:
        db_table = 'lexema_app_notifications'
        ordering = ['-created_at']
        verbose_name = _('Уведомление')
        verbose_name_plural = _('Уведомления')

    def __str__(self):
        return f'{self.get_notification_type_display()} к {self.recipient}'

    def mark_as_read(self):
        self.is_read = True
        self.save()

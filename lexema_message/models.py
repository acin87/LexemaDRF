from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from lexema_notification.models import Notification, NotificationType


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sender",
        verbose_name=_("Отправитель сообщения"),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recipient",
        verbose_name=_("Получатель сообщения"),
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    notifications = GenericRelation(Notification)

    class Meta:
        db_table = "lexema_app_message"
        verbose_name = _("Сообщение")
        verbose_name_plural = _("Сообщения")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{_("Сообщение от")} {self.sender} к {self.recipient}"

    def mark_as_read(self):
        """Пометить сообщение и связанные уведомления как прочитанные."""
        if not self.is_read:
            self.is_read = True
            self.save()
            # Помечаем все уведомления для этого сообщения как прочитанные
            self.notifications.filter(is_read=False).update(is_read=True)

    def create_notification(self):
        """Создать уведомление о новом сообщении."""
        from django.contrib.contenttypes.models import ContentType

        # Проверяем, чтобы отправитель не получал уведомление о своём сообщении
        if self.sender != self.recipient:
            Notification.objects.create(
                recipient=self.recipient,
                sender=self.sender,
                notification_type=NotificationType.NEW_MESSAGE,
                message=f"{_("Новое сообщение от")} {self.sender.first_name} {self.sender.last_name}",
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.id,
                extra_data={
                    "message_preview": (
                        self.content[:50] + "..."
                        if len(self.content) > 50
                        else self.content
                    )
                },
            )

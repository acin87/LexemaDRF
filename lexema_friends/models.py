from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError


class Friend(models.Model):
    """Модель друзей с уведомлениями"""

    class Status(models.TextChoices):
        PENDING = "pending", _("Отправлено")
        ACCEPTED = "accepted", _("Подтверждено")
        REJECTED = "rejected", _("Отклонено")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friends_sent",
        verbose_name=_("Пользователь"),
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friends_received",
        verbose_name=_("Друг"),
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Статус"),
    )
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    class Meta:
        db_table = "lexema_app_friends"
        verbose_name = _("Друг")
        verbose_name_plural = _("Друзья")
        unique_together = ("user", "friend")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("friend")),
                name="user_cannot_be_friend",
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.friend} ({self.status})"

    def send_notification(self, status):
        """Основной метод отправки уведомлений"""
        from lexema_notification.models import Notification, NotificationType

        notification_type = {
            self.Status.PENDING: NotificationType.FRIEND_REQUEST,
            self.Status.ACCEPTED: NotificationType.FRIEND_ACCEPTED,
            self.Status.REJECTED: NotificationType.FRIEND_REJECTED,
        }.get(status)

        if not notification_type:
            return

        Notification.objects.create(
            recipient=self.friend if status == self.Status.PENDING else self.user,
            sender=self.user if status == self.Status.PENDING else self.friend,
            notification_type=notification_type,
            extra_data={"friendship_id": self.id, "status": status},
        )

    def send_accept_notification(self):
        """Дополнительное уведомление при принятии дружбы"""
        from lexema_notification.models import Notification, NotificationType

        # Уведомление инициатору
        Notification.objects.create(
            recipient=self.user,
            sender=self.friend,
            notification_type=NotificationType.FRIEND_ACCEPTED,
            extra_data={"friendship_id": self.id, "status": self.Status.ACCEPTED},
        )

    def remove_friendship(self, initiator):
        """Удаляет запись о дружбе с проверкой прав и отправкой уведомления.

        :param initiator: Кто инициировал удаление (объект User)
        :raises ValidationError: Если initiator не участник дружбы
        """
        # Проверяем, что инициатор — один из участников
        if initiator not in [self.user, self.friend]:
            raise ValidationError(_("Вы не можете удалить эту дружбу"))

        # Отправляем уведомление (если нужно)
        self._send_removal_notification(initiator)

        # Удаляем запись
        self.delete()

    def _send_removal_notification(self, initiator):
        """Приватный метод для отправки уведомления об удалении."""
        from lexema_notification.models import Notification, NotificationType

        recipient = self.friend if initiator == self.user else self.user

        Notification.objects.create(
            recipient=recipient,
            sender=initiator,
            notification_type=NotificationType.FRIEND_REMOVED,
            extra_data={"friendship_id": self.id, "removed_by": initiator.id},
        )

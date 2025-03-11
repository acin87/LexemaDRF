from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Friends(models.Model):
    """Модель друзей"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friends_sent",
    )
    friend = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friends_received"
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="pending",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Мета класс для модели Friends"""
        db_table = "lexema_app_friends"
        verbose_name = "Друзья"
        verbose_name_plural = "Friends"
        unique_together = ("user", "friend")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(user=models.F("friend")),
                name="user_cannot_be_friend",
            ),
        ]

    def __str__(self):
        return f"{self.user} -> {self.friend} ({self.status})"

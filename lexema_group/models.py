from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class LexemaGroups(models.Model):
    """Модель групп"""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ Метаданные модели групп """ ""
        ordering = ["-created_at"]
        db_table = "lexema_app_groups"
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self) -> str:
        return f"{self.name}"


class GroupMembership(models.Model):
    """Модель для участия в группе"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="group_memberships")
    group = models.ForeignKey(LexemaGroups, on_delete=models.CASCADE, related_name="members")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lexema_app_group_memberships"
        unique_together = ("user", "group")
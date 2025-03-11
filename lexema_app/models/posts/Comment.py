"""Модель комментариев"""

from django.db import models
from django.contrib.auth.models import User

from lexema_app.models.posts.Posts import Posts


class Comment(models.Model):
    """Модель комментариев"""

    id = models.AutoField(primary_key=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    likes = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f"{self.id}: {self.body}..."

    class Meta:
        """Метаданные модели комментария"""

        db_table = "lexema_app_comments"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

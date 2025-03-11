"""Модель поста"""

from django.db import models
from django.contrib.auth.models import User

from lexema_app.models.groups.Groups import LexemaGroups




class Posts(models.Model):
    """Модель поста"""

    id = models.AutoField(primary_key=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(
        LexemaGroups,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_posts",
    )
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    video_urls = models.JSONField(null=True, blank=True)
    original_post = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reposted_by",
    )
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content}"

    class Meta:
        """Метаданные модели поста"""

        db_table = "lexema_app_posts"
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]

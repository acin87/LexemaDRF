"""Модуль для импорта моделей"""

import os
import uuid
from django.db import models
from django.contrib.auth.models import User

from lexema_group.models import LexemaGroups


class Post(models.Model):
    """Модель поста"""

    id = models.AutoField(primary_key=True)
    content = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_posts"
    )
    group = models.ForeignKey(
        LexemaGroups,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="group_posts",
    )
    video_urls = models.JSONField(null=True, blank=True)
    original_post = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reposted_by",
    )
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.pk} - {self.author} / {self.group} - {self.content}"  # pylint: disable=no-member

    class Meta:
        """Метаданные модели поста"""

        db_table = "lexema_app_posts"
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]


def post_image_upload_to(instance, filename):
    """
    Генерация пути и имени файла для изображения поста.
    """

    ext = filename.split(".")[-1]

    new_filename = (
        f"image_{instance.post.id}_{instance.post.author.pk}_{uuid.uuid4().hex}.{ext}"
    )

    return os.path.join("posts/images/", new_filename)


class PostImage(models.Model):
    """Модель изображения поста"""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=post_image_upload_to)

    def __str__(self):
        return self.image.name

    class Meta:
        """Метаданные модели изображения поста"""

        db_table = "lexema_app_post_images"
        verbose_name = "Изображение поста"
        verbose_name_plural = "Изображения поста"

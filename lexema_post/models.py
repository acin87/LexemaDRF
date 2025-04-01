"""Модуль для импорта моделей"""

import os
import textwrap
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q

from lexema_friends.models import Friends
from lexema_group.models import LexemaGroups
from lexema_user.models import User


class Post(models.Model):
    """Модель поста"""

    id = models.AutoField(primary_key=True)
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_posts"
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
    views = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def short_content(self):
        """
        Возвращает короткий текст поста.
        """
        if self.original_post:
            return f"Репост поста"
        if self.content is None:
            return self.content
        if len(self.content) <= 100:
            return self.content

        return textwrap.shorten(self.content, width=100, placeholder="...")

    def __str__(self):
        return f"{self.id} - {self.author} / {self.group} - {self.short_content()}"

    class Meta:
        """Метаданные модели поста"""

        db_table = "lexema_app_posts"
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]

    def send_notification(self):
        friends = Friends.objects.filter(
            Q(user=self.author) | Q(friend=self.author),
            Q(status="accepted"))
        for friend in friends:
            self._send_new_post_notification(friend.user, friend.friend)

    def _send_new_post_notification(self, initiator, recipient):
        """Приватный метод для отправки уведомления о новом посте друга."""
        from lexema_notification.models import Notification, NotificationType

        Notification.objects.create(
            recipient=recipient,
            sender=initiator,
            notification_type=NotificationType.FRIEND_NEW_POST,
            extra_data={
                'post_id': self.id,
                'author_id': initiator.pk,
            }
        )


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


class PostLike(models.Model):
    """Модель лайков поста. Один пользователь может лайкнуть пост только один раз."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes',
        verbose_name='Пользователь'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Пост'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    reaction_type = models.CharField(
        max_length=20,
        default='like',
        choices=[('like', 'Like'), ('dislike', 'Dislike')],
        verbose_name='Тип реакции'
    )

    class Meta:
        verbose_name = 'Лайк поста'
        verbose_name_plural = 'Лайки постов'
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.reaction_type} - {self.post.id}'

    def clean(self):
        if self.user == self.post.author:
            raise ValidationError('Вы не можете лайкать свои собственные посты')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

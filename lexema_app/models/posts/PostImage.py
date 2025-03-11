"""Модуль модели изображения поста"""

from django.db import models

from lexema_app.models.posts.Posts import Posts


class PostImage(models.Model):
    """Модель изображения поста"""

    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="posts/images/")

    def __str__(self):
        return self.image.name
    
    class Meta:
        """Метаданные модели изображения поста"""
        db_table = "lexema_app_post_images"
        verbose_name = "Изображение поста"
        verbose_name_plural = "Изображения поста"
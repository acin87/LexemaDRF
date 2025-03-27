import os
import textwrap
import uuid

from django.db import models

from lexema_post.models import Post
from lexema_server import settings


# Create your models here.
class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, related_name='comments_author')
    content = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True , related_name='replies')
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Пост - {self.post_id} / Коммент - {self.id}"

    class Meta:
        db_table = 'lexema_app_comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

def comment_image_upload_to(instance, filename):

    ext = filename.split('.')[-1]
    new_filename = f"image_{instance.comment.id}_{instance.comment.author.pk}_{uuid.uuid4().hex}.{ext}"
    return os.path.join("posts/comments/images/", new_filename)


class CommentImages(models.Model):
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE, blank=True, related_name='images')
    image = models.ImageField(upload_to=comment_image_upload_to, blank=True)

    def __str__(self):
        return f"{self.comment.id} - {self.comment.post_id} --- {textwrap.shorten(self.comment.content, width=100, placeholder="...")}"

    class Meta:
        db_table = 'lexema_app_comment_images'
        verbose_name = 'Изображение комментария'
        verbose_name_plural = 'Изображения комментариев'


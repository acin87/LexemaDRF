""" Модуль групп """
from django.db import models
from django.contrib.auth.models import User

class LexemaGroups(models.Model):
    """ Модель групп """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    cover_image_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """ Метаданные модели групп """""
        ordering = ['-created_at']
        db_table = 'lexema_app_groups'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
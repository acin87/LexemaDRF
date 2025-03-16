import os
import uuid

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.
def profile_image_upload_to(instance, filename):

    ext = filename.split(".")[-1]
    new_filename = f"img_{instance.user.id}_{uuid.uuid4().hex}.{ext}"

    return os.path.join("users/images/", new_filename)


class Profile(models.Model):
    """Модель профиля"""

    gender_choices = (
        ("male", "Мужской"),
        ("female", "Женский"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(150)]
    )
    gender = models.CharField(max_length=50, choices=gender_choices,blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    company = models.JSONField(blank=True, null=True)

    class Meta:
        """Мета класс для модели Profile"""
        db_table = "lexema_app_profile"
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

class ProfileImages(models.Model):
    """Модель изображений профиля"""

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    avatar_image = models.ImageField(profile_image_upload_to, blank=True, null=True)
    main_page_image = models.ImageField(profile_image_upload_to, blank=True, null=True)


    class Meta:
        """Мета класс для модели ProfileImages"""
        db_table = "lexema_app_profile_images"
        verbose_name = "Изображение профиля"
        verbose_name_plural = "Изображения профилей"
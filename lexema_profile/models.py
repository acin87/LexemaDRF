import os
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from PIL import Image


# Create your models here.
def profile_image_upload_to(instance, filename):

    new_filename = f"img_{instance.profile.user.id}_{uuid.uuid4().hex}.webp"

    return os.path.join("users/images/", new_filename)


class Profile(models.Model):
    """Модель профиля"""

    gender_choices = (
        ("male", "Мужской"),
        ("female", "Женский"),
    )
    available_choices = (
        ("online", "Онлайн"),
        ("offline", "Оффлайн"),
    )
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_notification_read = models.DateTimeField(blank=True, null=True)
    available = models.CharField(
        max_length=50, choices=available_choices, blank=True, null=True
    )
    age = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(150)]
    )
    gender = models.CharField(
        max_length=50, choices=gender_choices, blank=True, null=True
    )
    signature = models.TextField(blank=True, null=True)
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
        return f"{self.user.first_name} {self.user.last_name} - {self.user.pk}"


class ProfileImages(models.Model):
    """Модель изображений профиля"""

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="images"
    )
    avatar_image = models.ImageField(
        upload_to=profile_image_upload_to, blank=True, null=True, name="avatar_image"
    )
    main_page_image = models.ImageField(
        upload_to=profile_image_upload_to, blank=True, null=True, name="main_page_image"
    )

    class Meta:
        """Мета класс для модели ProfileImages"""

        db_table = "lexema_app_profile_images"
        verbose_name = "Изображение профиля"
        verbose_name_plural = "Изображения профилей"

    def __str__(self):
        return (
            "Изображения профиля - "
            + self.profile.user.first_name
            + " "
            + self.profile.user.last_name
        )

    def resize_image(self, image_field, size=(300, 300)):
        """Изменяет размер изображения и конвертирует в WebP"""
        if image_field:
            img = Image.open(image_field.path)

            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            img.thumbnail(size)

            webp_path = image_field.path.replace(
                os.path.splitext(image_field.path)[1], ".webp"
            )
            img.save(webp_path, format="WEBP", quality=85)

            if not image_field.path.endswith(".webp"):
                os.remove(image_field.path)

            image_field.name = image_field.name.replace(
                os.path.splitext(image_field.name)[1], ".webp"
            )

    def save(self, *args, **kwargs):
        """Переопределяем метод save для изменения размера изображений и конвертации в WebP"""
        super().save(*args, **kwargs)  # Сначала сохраняем модель

        if self.avatar_image:
            self.resize_image(
                self.avatar_image, size=(300, 300)
            )  # Размер аватара 300x300

        if self.main_page_image:
            self.resize_image(self.main_page_image, size=(1900, 475))  # Размер 800x600

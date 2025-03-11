"""Users model"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Profiles(models.Model):
    """Класс для хранения информации о пользователях"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    patronymic = models.CharField(max_length=255, blank=True, null=True)
    age = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(150)]
    )
    gender = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar_image = models.CharField(max_length=255, blank=True, null=True)
    main_page_image = models.CharField(max_length=255, blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    company = models.JSONField(blank=True, null=True)

    class Meta:
        """Meta class for Users model"""

        db_table = "lexema_app_profiles"
        verbose_name = "Профиль"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.username} {self.surname} ({self.patronymic})"

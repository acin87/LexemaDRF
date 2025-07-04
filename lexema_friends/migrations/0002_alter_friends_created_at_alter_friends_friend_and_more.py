# Generated by Django 5.1.7 on 2025-03-29 17:28

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexema_friends", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="friends",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="Создано"
            ),
        ),
        migrations.AlterField(
            model_name="friends",
            name="friend",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="friends_received",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Друг",
            ),
        ),
        migrations.AlterField(
            model_name="friends",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Отправлено"),
                    ("accepted", "Подтверждено"),
                    ("rejected", "Отклонено"),
                ],
                default="pending",
                max_length=50,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="friends",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Обновлено"),
        ),
        migrations.AlterField(
            model_name="friends",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="friends_sent",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
    ]

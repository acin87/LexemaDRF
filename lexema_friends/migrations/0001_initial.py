# Generated by Django 5.1.7 on 2025-03-21 18:50

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Friends",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Отправлено"),
                            ("accepted", "Подтверждено"),
                            ("rejected", "Отклонено"),
                        ],
                        default="pending",
                        max_length=50,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "friend",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="friends_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="friends_sent",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Друг",
                "verbose_name_plural": "Друзья",
                "db_table": "lexema_app_friends",
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("user", models.F("friend")), _negated=True),
                        name="user_cannot_be_friend",
                    )
                ],
                "unique_together": {("user", "friend")},
            },
        ),
    ]

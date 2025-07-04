# Generated by Django 5.1.7 on 2025-03-29 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lexema_notification", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.CharField(
                choices=[
                    ("friend_request", "Запрос в друзья"),
                    ("friend_accepted", "Запрос принят"),
                    ("friend_rejected", "Запрос отклонён"),
                    ("new_message", "Новое сообщение"),
                    ("typing_started", "Печатает..."),
                ],
                max_length=50,
                verbose_name="Notification Type",
            ),
        ),
    ]

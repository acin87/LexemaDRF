# Generated by Django 5.1.7 on 2025-04-03 17:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("lexema_group", "0001_initial"),
        ("lexema_post", "0004_remove_post_dislikes_remove_post_likes_postlike"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="LexemaGroups",
            new_name="LexemaGroup",
        ),
    ]

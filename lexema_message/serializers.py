from django.conf import settings
from rest_framework import serializers

from lexema_message.models import Message
from lexema_profile.models import Profile, ProfileImages


class FullMessageSerializer(serializers.ModelSerializer):
    """Полный сериализатор сообщения"""

    class Meta:
        model = Message
        fields = ["id", "sender", "recipient", "content", "timestamp", "is_read"]
        read_only_fields = ["id", "timestamp", "is_read"]

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        message.create_notification()  # Создаём уведомление
        return message


class ShortMessageSerializer(serializers.ModelSerializer):
    """Короткий сериализатор сообщения"""

    short_content = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "recipient",
            "short_content",
            "content",
            "timestamp",
            "is_read",
            "unread_count",
        ]
        read_only_fields = ["id", "sender", "timestamp", "is_read"]

    def get_unread_count(self, obj):
        """Возвращаем количество непрочитанных сообщений"""
        return Message.objects.filter(recipient=obj.recipient, is_read=False).count()

    def get_short_content(self, obj):
        """Возвращаем первые 50 символов с '...' если контент длинный"""
        return obj.content[:100] + ("..." if len(obj.content) > 100 else "")

    def get_sender(self, obj):
        """Возвращаем имя пользователя для отправителя"""
        user = {
            "id": obj.sender.id,
            "full_name": obj.sender.first_name + " " + obj.sender.last_name,
            "username": obj.sender.username,
            "avatar": f"http://{settings.ALLOWED_HOSTS[0]}:8000{self._get_avatar_url(obj.sender)}",
        }
        return user

    def get_recipient(self, obj):
        """Возвращаем имя пользователя для получателя"""
        user = {
            "id": obj.recipient.id,
            "full_name": obj.recipient.first_name + " " + obj.recipient.last_name,
            "username": obj.recipient.username,
            "avatar": f"http://{settings.ALLOWED_HOSTS[0]}:8000{self._get_avatar_url(obj.recipient)}",
        }
        return user

    def _get_avatar_url(self, user):
        """Возвращаем аватар пользователя"""
        avatar = Profile.objects.filter(user=user).select_related("images").first()

        if avatar and avatar.images.avatar_image:
            return avatar.images.avatar_image.url
        return None

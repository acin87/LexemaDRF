from rest_framework import serializers

from lexema_message.models import Message
from lexema_profile.models import Profile, ProfileImages


class FullMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ["id", "sender", "recipient", "content", "timestamp", "is_read"]
        read_only_fields = ["id", "sender", "timestamp", "is_read"]

    def create(self, validated_data):
        message = Message.objects.create(**validated_data)
        message.create_notification()  # Создаём уведомление
        return message


class ShortMessageSerializer(serializers.ModelSerializer):

    short_content = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
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
        """Возвращаем первые 100 символов с '...' если контент длинный"""
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")

    def get_sender(self, obj):
        """Возвращаем имя пользователя"""
        profile = (
            Profile.objects.filter(user=obj.sender).select_related("images").first()
        )

        user = {
            "id": obj.sender.id,
            "full_name": obj.sender.first_name + " " + obj.sender.last_name,
            "avatar": profile.images.avatar_image,
        }
        return user

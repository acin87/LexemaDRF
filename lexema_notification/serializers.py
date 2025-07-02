from rest_framework import serializers

from lexema_profile.models import Profile
from .models import Notification, NotificationType


class NotificationSerializer(serializers.ModelSerializer):
    notification_type = serializers.SerializerMethodField()
    sender_info = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "message",
            "is_read",
            "created_at",
            "extra_data",
            "sender_info",
        ]
        read_only_fields = fields

    def get_notification_type(self, obj):
        return {
            "code": obj.notification_type,
            "display": obj.get_notification_type_display(),
        }

    def get_sender_info(self, obj):
        if not obj.sender:
            return None

        full_name = (
            obj.sender.get_full_name()
            if obj.sender.get_full_name()
            else obj.sender.username
        )

        return {
            "id": obj.sender.id,
            "full_name": full_name,
            "avatar": self._get_avatar_url(obj.sender),
        }

    def _get_avatar_url(self, user):
        avatar = Profile.objects.filter(user=user).select_related("images").first()

        if avatar and avatar.images.avatar_image:
            return avatar.images.avatar_image.url
        return None

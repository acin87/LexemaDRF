from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from rest_framework import serializers

from lexema_friends.models import Friends
from lexema_profile.models import ProfileImages

User = get_user_model()

class UserSerializerWithAvatar(serializers.ModelSerializer):

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'is_staff', 'is_active', 'avatar', 'first_name', 'last_name')

    @staticmethod
    def get_avatar(obj):
        """Метод для получения аватара пользователя"""
        profile = obj.profile
        if not profile:
            return None

        profile_image = ProfileImages.objects.filter(profile=profile).first()
        if profile_image and profile_image.avatar_image:
            return profile_image.avatar_image.url
        return None

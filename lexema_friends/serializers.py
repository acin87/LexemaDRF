from django.db.models import Q
from rest_framework import serializers
from lexema_friends.models import Friend
from lexema_group.models import GroupMembership
from lexema_post.models import Post
from lexema_profile.models import Profile
from lexema_profile.serializers import (
    ProfileUpcomingBirthdaySerializer,
    ProfileImagesSerializer,
)


class FriendsSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    friends_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()
    friend_friends_data = serializers.SerializerMethodField()
    isFilledProfile = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = [
            "full_name",
            "friends_count",
            "posts_count",
            "groups_count",
            "friend_id",
            "friend_friends_data",
            "avatar",
            "profile_image",
            "isFilledProfile",
            "last_login",
        ]

    def validate(self, data):
        # Проверка, что пользователь не отправляет запрос сам себе
        if self.context["request"].user == data["friend"]:
            raise serializers.ValidationError("Нельзя добавить себя в друзья")
        return data

    def get_avatar(self, obj):
        """Возвращаем аватар пользователя"""
        avatar = (
            Profile.objects.filter(user=obj.friend).select_related("images").first()
        )

        if avatar and avatar.images.avatar_image:
            return avatar.images.avatar_image.url
        return None

    def get_profile_image(self, obj):
        profile_image = (
            Profile.objects.filter(user=obj.friend).select_related("images").first()
        )

        if profile_image and profile_image.images.main_page_image:
            return profile_image.images.main_page_image.url
        return None

    def get_last_login(self, obj):
        return obj.friend.last_login

    def get_full_name(self, obj):
        return f"{obj.friend.first_name} {obj.friend.last_name}"

    def get_isFilledProfile(self, obj):
        return Profile.objects.filter(user=obj.friend).exists()

    @staticmethod
    def get_friends_count(obj):
        return Friend.objects.filter(friend=obj.friend, status="accepted").count()

    @staticmethod
    def get_posts_count(obj):
        return Post.objects.filter(author=obj.friend).count()

    @staticmethod
    def get_groups_count(obj):
        return GroupMembership.objects.filter(user=obj.friend).count()

    @staticmethod
    def get_friend_friends_data(obj):

        friend_friends = (
            Friend.objects.filter((Q(user=obj.friend) | Q(friend=obj.friend)))
            .select_related("friend")
            .prefetch_related("friend__profile__images")[:5]
        )

        friends_data = []
        for friend in friend_friends:

            friend_user = friend.user
            friend_data = {
                "id": friend_user.id,
                "full_name": f"{friend_user.first_name} {friend_user.last_name}",
                "avatar_image": friend_user.profile.images.avatar_image.url,
            }

            friends_data.append(friend_data)

        return friends_data


class UpcomingBirthDayFriendsSerializer(serializers.ModelSerializer):
    profile = ProfileUpcomingBirthdaySerializer(source="friend.profile", read_only=True)

    class Meta:
        model = Friend
        fields = ["profile"]

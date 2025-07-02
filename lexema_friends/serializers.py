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
    is_mutual = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = [
            "full_name",
            "username",
            "friends_count",
            "posts_count",
            "groups_count",
            "friend_id",
            "friend_friends_data",
            "avatar",
            "profile_image",
            "isFilledProfile",
            "last_login",
            "status",
            "is_mutual",
        ]

    def validate(self, data):
        # Проверка, что пользователь не отправляет запрос сам себе
        if self.context["request"].user == data["friend"]:
            raise serializers.ValidationError("Нельзя добавить себя в друзья")
        return data

    def get_is_mutual(self, obj):
        # Проверяем, был ли передан флаг mutual в контексте
        if not self.context.get("mutual_mode", False):
            return None

        # Получаем current_user из контекста
        current_user = self.context["request"].user

        # Проверяем, есть ли дружба между current_user и obj.friend
        return Friend.objects.filter(
            (Q(user=current_user) & Q(friend=obj.friend))
            | (Q(user=obj.friend) & Q(friend=current_user)),
            status="accepted",
        ).exists()

    def get_username(self, obj):
        return obj.friend.username

    def get_avatar(self, obj):
        """Возвращаем аватар пользователя"""
        profile = (
            Profile.objects.filter(user=obj.friend).select_related("images").first()
        )

        if hasattr(profile, "images"):
            if profile.images.avatar_image:
                return profile.images.avatar_image.url
        return None

    def get_profile_image(self, obj):
        profile = (
            Profile.objects.filter(user=obj.friend).select_related("images").first()
        )

        if hasattr(profile, "images") and hasattr(profile.images, "main_page_image"):
            if profile.images.main_page_image:
                return profile.images.main_page_image.url

        return None

    def get_last_login(self, obj):
        return obj.friend.last_login

    def get_full_name(self, obj):
        if obj.friend.first_name and obj.friend.last_name:
            return f"{obj.friend.first_name} {obj.friend.last_name}"
        return None

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
        friend_friends = Friend.objects.filter(
            Q(user=obj.friend) | Q(friend=obj.friend), status="accepted"
        ).select_related("friend", "friend__profile", "friend__profile__images")

        friends_data = []
        for friend in friend_friends:
            friend_user = friend.user if friend.user != obj.friend else friend.friend

            # исключаем себя из списка друзей
            if friend_user == obj.user or friend_user == obj.friend:
                continue

            full_name = f"{friend_user.first_name} {friend_user.last_name}"
            if full_name == " ":
                full_name = None
            # Базовые данные, которые всегда есть
            friend_data = {
                "id": friend_user.id,
                "full_name": full_name if full_name else friend_user.username,
                "avatar_image": None,  # По умолчанию None
            }

            # Проверяем наличие профиля и изображений
            if hasattr(friend_user, "profile") and friend_user.profile:
                if (
                    hasattr(friend_user.profile, "images")
                    and friend_user.profile.images
                ):
                    if friend_user.profile.images.avatar_image:
                        friend_data["avatar_image"] = (
                            friend_user.profile.images.avatar_image.url
                        )

            friends_data.append(friend_data)

        return friends_data


class FriendCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Friend
        fields = ["friend", "user", "status"]


class UpcomingBirthDayFriendsSerializer(serializers.ModelSerializer):
    profile = ProfileUpcomingBirthdaySerializer(source="friend.profile", read_only=True)

    class Meta:
        model = Friend
        fields = ["profile"]

from symtable import Class

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from lexema_friends.models import Friend
from lexema_group.models import GroupMembership
from lexema_post.models import Post
from lexema_profile.models import Profile, ProfileImages

User = get_user_model()


class ProfileImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileImages
        fields = ("avatar_image", "main_page_image")
        extra_args = {
            "avatar_image": {"required": False},
            "main_page_image": {"required": False},
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "is_staff", "is_superuser")


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    avatar = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    friends_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()
    is_friend = serializers.SerializerMethodField()
    friend_status = serializers.SerializerMethodField()
    friendship_id = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "user",
            "images",
            "education",
            "company",
            "gender",
            "age",
            "address",
            "available",
            "friends_count",
            "posts_count",
            "groups_count",
            "birth_date",
            "signature",
            "is_friend",
            "friend_status",
            "friendship_id",
            "avatar",
            "profile_image",
        ]

    @staticmethod
    def get_avatar(obj):
        if obj.images and obj.images.avatar_image:
            return obj.images.avatar_image.url
        return None

    @staticmethod
    def get_profile_image(obj):
        if obj.images and obj.images.main_page_image:
            return obj.images.main_page_image.url
        return None

    @staticmethod
    def get_friends_count(obj):
        return Friend.objects.filter(user=obj.user, status="accepted").count()

    @staticmethod
    def get_posts_count(obj):
        return Post.objects.filter(author=obj.user).count()

    @staticmethod
    def get_groups_count(obj):
        return GroupMembership.objects.filter(user=obj.user).count()

    def get_is_friend(self, obj):
        user = self.context["request"].user
        return Friend.objects.filter(
            Q(user=user, friend=obj.user) | Q(user=obj.user, friend=user),
            Q(status="accepted"),
        ).exists()

    def get_friend_status(self, obj):
        user = self.context["request"].user
        queryset = Friend.objects.filter(
            Q(user=user, friend=obj.user),
            Q(status="pending") | Q(status="accepted") | Q(status="rejected"),
        )

        status_choices = {
            "pending": {"code": 0, "name": "Отправлено"},
            "accepted": {"code": 1, "name": "Подтверждено"},
            "rejected": {"code": 2, "name": "Отклонено"},
        }

        if queryset.exists():
            first_result = queryset.first()
            return status_choices[first_result.status]

        return None

    def get_friendship_id(self, obj):
        user = self.context["request"].user
        queryset = Friend.objects.filter(
            Q(user=user, friend=obj.user) | Q(user=obj.user, friend=user),
            Q(status="pending") | Q(status="accepted") | Q(status="rejected"),
        )

        if queryset.exists():
            first_result = queryset.first()
            return first_result.id

        return None


class ProfileUpcomingBirthdaySerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    images = ProfileImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "images", "birth_date")

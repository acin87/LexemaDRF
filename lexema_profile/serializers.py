from symtable import Class

from django.contrib.auth import get_user_model
from rest_framework import serializers

from lexema_friends.models import Friends
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


class ProfileForFriendFeedSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    images = ProfileImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "images")


class ProfileSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    images = ProfileImagesSerializer(many=True, read_only=True)
    friends_count = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    groups_count = serializers.SerializerMethodField()

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
        ]

    def get_friends_count(self, obj):
        return Friends.objects.filter(user=obj.user, status="accepted").count()

    def get_posts_count(self, obj):
        return Post.objects.filter(author=obj.user).count()

    def get_groups_count(self, obj):
        return GroupMembership.objects.filter(user=obj.user).count()

class ProfileUpcomingBirthdaySerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    images = ProfileImagesSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("user", "images", "birth_date")
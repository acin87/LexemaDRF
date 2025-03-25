from django.contrib.auth import get_user_model
from rest_framework import serializers
from lexema_post.models import Post, PostImage
from lexema_profile.models import ProfileImages

User = get_user_model()


class PostImageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели PostImage"""

    class Meta:
        """Метаданные сериализатора"""

        model = PostImage
        fields = ["image"]
        extra_args = {"image": {"required": False}}


class AuthorSerializer(serializers.ModelSerializer):
    """Класс сериализатора для модели пользователя"""

    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "avatar",
        )

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


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""

    images = PostImageSerializer(many=True, read_only=True)
    author = AuthorSerializer()
    reposts = serializers.SerializerMethodField()

    class Meta:
        """Метаданные сериализатора"""

        model = Post
        fields = [
            "id",
            "content",
            "author",
            "group",
            "video_urls",
            "original_post",
            "likes",
            "dislikes",
            "views",
            "comments_count",
            "created_at",
            "images",
            "reposts"
        ]

    @staticmethod
    def get_reposts(obj):
        return Post.objects.filter(original_post=obj).count()


class PostCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления поста"""

    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "group",
            "video_urls",
            "original_post",
            "images",
        ]
        extra_kwargs = {
            "author": {"read_only": True},
        }
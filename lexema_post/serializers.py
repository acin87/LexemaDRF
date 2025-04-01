from django.contrib.auth import get_user_model
from rest_framework import serializers
from lexema_post.models import Post, PostImage
from lexema_profile.models import ProfileImages
from lexema_profile.serializers import ProfileSerializer

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
    reposts_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    signature = serializers.SerializerMethodField()

    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

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
            "views",
            "comments_count",
            "created_at",
            "images",
            "reposts_count",
            "signature",
            "likes_count",
            "dislikes_count",
            "user_reaction",
            "is_liked",
        ]

    @staticmethod
    def get_reposts_count(obj):
        return Post.objects.filter(original_post=obj).count()

    @staticmethod
    def get_comments_count(obj):
        return obj.comments.count()

    @staticmethod
    def get_signature(obj):
        return obj.author.profile.signature

    @staticmethod
    def get_likes_count(obj):
        """Количество лайков поста"""
        return obj.likes.filter(reaction_type='like').count()


    @staticmethod
    def get_dislikes_count(obj):
        """Количество дизлайков поста"""
        return obj.likes.filter(reaction_type='dislike').count()


    def get_user_reaction(self, obj):
        """Реакция текущего пользователя на пост"""
        request = self.context.get('request')
        if not request:
            print("Request object is missing in serializer context")
            return None

        if not hasattr(request, 'user'):
            print("Request has no user attribute")
            return None

        user = request.user
        if not user.is_authenticated:
            return None

        try:
            like = obj.likes.filter(user=user).first()
            return like.reaction_type if like else None
        except Exception as e:
            print(f"Error getting reaction: {str(e)}")
            return None

    def get_is_liked(self, obj):
        """Для обратной совместимости"""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return False

        user = request.user
        if not user:
            return False

        try:
            return obj.likes.filter(user=user, reaction_type='like').exists()
        except Exception as e:
            print(f"Error checking like: {str(e)}")
            return False


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
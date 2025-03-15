from rest_framework import serializers
from lexema_post.models import Post, PostImage
from lexema_post.serializers.author_serializer import AuthorSerializer


class PostImageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели PostImage"""

    class Meta:
        """Метаданные сериализатора"""

        model = PostImage
        fields = ["image"]
        extra_args = {"image": {"required": False}}


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""

    images = PostImageSerializer(many=True, read_only=True)
    author = AuthorSerializer()

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
            "comments",
            "created_at",
            "images",
        ]

"""Сериализатор для модели Posts"""

from rest_framework import serializers

from lexema_app.models.posts.PostImage import PostImage
from lexema_app.models.posts.Posts import Posts


class PostImageSerializer(serializers.ModelSerializer):
    """Сериализатор для модели PostImage"""

    class Meta:
        """Метаданные сериализатора"""

        model = PostImage
        fields = ["image"]


class PostsSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Posts"""

    images = PostImageSerializer(many=True, read_only=True)

    class Meta:
        """Метаданные сериализатора"""

        model = Posts
        fields = ['id', 'title', 'content', 'author', 'images', 'created_at']
        extra_kwargs = {
            'images': {'required': False},  # Поле images не обязательное
        }

from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination

from lexema_comment.models import Comments
from lexema_user.serializers import UserSerializerWithAvatar


class CommentsSerializer(serializers.ModelSerializer):

    user = UserSerializerWithAvatar(source="author",read_only=True)

    class Meta:
        model = Comments
        fields = ('id', 'content', 'parent_id', 'user', 'likes', 'post_id', 'created_at', 'updated_at')


class RecursiveRootCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода древовидных комментариев.
    Рекурсивно выводит только один уровень дочерних комментариев.
    """
    user = UserSerializerWithAvatar(source="author", read_only=True)
    replies = serializers.SerializerMethodField()
    child_count = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = (
            'id',
            'content',
            'parent_id',
            'user',
            'likes',
            'post_id',
            'created_at',
            'updated_at',
            'replies',
            'child_count'
        )


    def get_replies(self, instance):
        """
        Метод для получения дочерних комментариев только первого уровня.
        """
        if instance.parent is None:
            children = instance.replies.all()[:1]
            serializer = RecursiveRootCommentSerializer(children, many=True, context=self.context)
            return serializer.data
        else:
            return []

    @staticmethod
    def get_child_count(instance):
        """
        Метод для получения количества дочерних комментариев.
        """
        return instance.replies.count()


class RecursiveChildCommentsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода древовидных комментариев.
    Рекурсивно выводит все дочерние комментарии.
    """
    user = UserSerializerWithAvatar(source="author", read_only=True)
    replies = serializers.SerializerMethodField()
    child_count = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = (
            'id',
            'content',
            'parent_id',
            'user',
            'likes',
            'post_id',
            'created_at',
            'updated_at',
            'replies',
            'child_count'
        )

    def get_replies(self, instance):
        """
        Метод для получения всех дочерних комментариев с рекурсией.
        """
        children = instance.replies.all().order_by('created_at')[:1]
        serializer = type(self)(children, many=True)
        return serializer.data

    @staticmethod
    def get_child_count(instance):
        """
        Метод для получения количества дочерних комментариев.
        """
        return instance.replies.count()
from django.db.models import OuterRef, Subquery
from django.db import transaction

from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.pagination import LimitOffsetPagination

from lexema_friends.models import Friend
from lexema_group.models import GroupMembership
from lexema_post.models import Post, PostImage, PostLike
from lexema_post.serializers import PostSerializer, PostCreateSerializer


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение, которое позволяет редактировать или удалять пост только его автору."""

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if request.method == "PATCH" and "views" in request.data:
            return True
        return obj.author == request.user


class MainFeedView(APIView):
    """Вью для главной ленты"""

    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user = request.user

        user_groups = GroupMembership.objects.filter(user=user).values_list(
            "group", flat=True
        )
        group_posts = Post.objects.filter(group__in=user_groups).order_by(
            "-created_at"
        )[
            :10
        ]  # не забыть изменить на 1

        friends = Friend.objects.filter(user=user, status="accepted").values_list(
            "friend", flat=True
        )

        latest_posts = (
            Post.objects.filter(author=OuterRef("author"))
            .order_by("-created_at")
            .values("id")[:10]  # не забыть изменить на 1
        )

        friends_posts = Post.objects.filter(
            id__in=Subquery(latest_posts), author__in=friends
        ).order_by("-created_at")

        if user.is_staff:
            posts = Post.objects.all().order_by("-created_at")
        else:
            posts = (group_posts | friends_posts).distinct().order_by("-created_at")

        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(
            paginated_posts, many=True, context={"request": request}
        )

        response = paginator.get_paginated_response(serializer.data)

        return response


class PostViewSet(viewsets.ModelViewSet):
    """Вью для списка постов"""

    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update"]:
            return PostCreateSerializer
        return PostSerializer

    def get_serializer_context(self):
        """Добавляем request в контекст сериализатора"""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Post.objects.all().order_by("-created_at")

        # Оптимизация запросов
        queryset = queryset.select_related("author", "group", "original_post")
        queryset = queryset.prefetch_related("images", "likes")

        # Фильтрация по параметрам
        user_id = self.kwargs.get("user_id")
        group_id = self.kwargs.get("group_id")
        friend_id = self.kwargs.get("friend_id")

        if user_id:
            return queryset.filter(author_id=user_id)
        elif group_id:
            return queryset.filter(group_id=group_id)
        elif friend_id:
            return queryset.filter(author_id=friend_id)

        return queryset if self.request.user.is_staff else Post.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        post_serializer = self.get_serializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)
        self.perform_create(post_serializer)

        images_data = request.FILES.getlist("images")
        self._handle_images(images_data, post_serializer.instance)

        return Response(post_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"detail": "У вас нет прав на удаление этого поста"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Обработка просмотров
        if "views" in request.data and instance.author != request.user:
            instance.views += 1
            instance.save(update_fields=["views"])
            return Response(status=status.HTTP_200_OK)

        # Обработка лайков
        if "like_action" in request.data:
            return self._handle_like_action(instance, request.data["like_action"])

        # Обновление поста
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Обработка изображений
        if "new_images" in request.data:
            self._handle_images_update(instance, request)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def _handle_like_action(self, post, action):
        """Обработка действий с лайками"""
        user = self.request.user

        if user == post.author:
            return Response(
                {"detail": "Вы не можете лайкать свои собственные посты"},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            like, created = PostLike.objects.get_or_create(
                user=user, post=post, defaults={"reaction_type": action}
            )

            if not created:
                if like.reaction_type == action:
                    like.delete()  # Удаляем если повторный клик
                else:
                    like.reaction_type = action
                    like.save()

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def _handle_images(images_data, post):
        """Создание новых изображений"""
        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)

    def _handle_images_update(self, post, request):
        """Обновление изображений поста"""
        current_images = post.images.all()
        frontend_images = request.data["new_images"]

        # Удаление изображений
        if isinstance(frontend_images, list):
            frontend_image_urls = {
                img["image"] for img in frontend_images if "image" in img
            }
            images_to_delete = [
                img
                for img in current_images
                if img.image.url not in frontend_image_urls
            ]
            PostImage.objects.filter(
                id__in=[img.id for img in images_to_delete]
            ).delete()

        # Добавление новых изображений
        new_images_data = request.FILES.getlist("new_images")
        self._handle_images(new_images_data, post)


class RepostRetrieveView(generics.RetrieveAPIView):
    """Метод для получения репоста поста"""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        post_id = kwargs.get("post_id")
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

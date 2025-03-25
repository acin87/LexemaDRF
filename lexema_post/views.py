from django.db.models import OuterRef, Subquery
from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination

from lexema_friends.models import Friends
from lexema_group.models import GroupMembership
from lexema_post.models import Post, PostImage
from lexema_post.serializers import PostSerializer, PostCreateSerializer


class IsAuthorOrReadOnly(BasePermission):
    """Разрешение, которое позволяет редактировать или удалять пост только его автору."""
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        if request.method == "PATCH" and "views" in request.data:
            return True
        return obj.author == request.user

class MainFeedView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user = request.user

        user_groups = GroupMembership.objects.filter(user=user).values_list(
            "group", flat=True
        )
        group_posts = Post.objects.filter(group__in=user_groups).order_by(
            "-created_at"
        )[:10]

        friends = Friends.objects.filter(user=user, status="accepted").values_list(
            "friend", flat=True
        )

        latest_posts = (
            Post.objects.filter(author=OuterRef("author"))
            .order_by("-created_at")
            .values("id")[:10]
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

        serializer = PostSerializer(paginated_posts, many=True)

        response = paginator.get_paginated_response(serializer.data)

        return response





class PostViewSet(viewsets.ModelViewSet):
    """Модель для списка постов"""

    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination


    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return PostCreateSerializer
        return PostSerializer


    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    def get_queryset(self):
        user_id = self.kwargs.get('user_id') # profile/(?P<user_id>\d+)/posts
        group_id = self.kwargs.get('group_id') # group/(?P<group_id>\d+)/posts
        friend_id = self.kwargs.get('friend_id') # friend/(?P<friend_id>\d+)/posts
        if self.request.user.is_staff:
            return Post.objects.all().order_by("-created_at")
        elif user_id:
            return Post.objects.filter(author_id=user_id).order_by('-created_at')
        elif group_id:
            return Post.objects.filter(group_id=group_id).order_by('-created_at')
        elif friend_id:
            return Post.objects.filter(author_id=friend_id).order_by('-created_at')
        return Post.objects.none()


    def create(self, request, *args, **kwargs):
        post_data = request.data
        images_data = request.FILES.getlist("images")

        post_serializer = self.get_serializer(data=post_data)
        post_serializer.is_valid(raise_exception=True)

        self.perform_create(post_serializer)
        self.create_images(images_data, post_serializer.instance)

        return Response(post_serializer.data, status=status.HTTP_201_CREATED)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.author != request.user and not request.user.is_staff:
            raise PermissionDenied("У вас нет прав на выполнение данной операции.")

        return super().destroy(request, *args, **kwargs)


    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user and request.data.get("views") is not None:
            with transaction.atomic():
                instance.views += 1
                instance.save(update_fields=["views"])
                return Response(status=status.HTTP_200_OK)

        post_serializer = self.get_serializer(instance, data=request.data, partial=True)

        post_serializer.is_valid(raise_exception=True)

        self.perform_update(post_serializer)

        if "new_images" in request.data:
            current_images = instance.images.all()

            # Получаем изображения, пришедшие с фронта
            frontend_images = request.data["new_images"]

            if "image" in frontend_images:
                print(frontend_images)
                frontend_image_urls = {
                    img["image"] for img in frontend_images if img["image"]
                }

                # Удаляем изображения, которые есть в базе, но отсутствуют на фронте
                images_to_delete = [
                    img
                    for img in current_images
                    if img.image.url not in frontend_image_urls
                ]
                PostImage.objects.filter(
                    id__in=[img.id for img in images_to_delete]
                ).delete()

            new_images_data = request.FILES.getlist("new_images")

            self.create_images(new_images_data, instance)
        updated_instance = self.get_object()

        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @staticmethod
    def create_images(images_data, post):

        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)
        return Response(status=status.HTTP_201_CREATED)

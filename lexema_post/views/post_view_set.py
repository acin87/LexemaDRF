from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from lexema_post.models import Post, PostImage
from lexema_post.serializers.post_serializer import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Модель для списка постов"""

    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer

    def check_author_permission(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("У вас нет прав на выполнение этой операции.")

    def get_serializer(self, *args, **kwargs):
        if self.action in ["create", "update", "partial_update"]:
            kwargs["data"] = kwargs.get("data", {}).copy()
            kwargs["data"]["author"] = self.request.user.pk
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_staff:  # Администраторы видят все посты
            return Post.objects.all().order_by("-created_at")
        else:  # Обычные пользователи видят только свои посты
            return Post.objects.filter(author=self.request.user.pk).order_by(
                "-created_at"
            )

    def create(self, request, *args, **kwargs):
        post_data = request.data
        images_data = request.FILES.getlist("images")

        post_serializer = self.get_serializer(data=post_data)
        post_serializer.is_valid(raise_exception=True)
        post = post_serializer.save()

        self.create_images(images_data, post)
        return Response(post_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        self.check_author_permission(instance)

        return super().update(request, *args, **kwargs)

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

        self.check_author_permission(instance)
        post_serializer = self.get_serializer(instance, data=request.data, partial=True)

        post_serializer.is_valid(raise_exception=True)

        self.perform_update(post_serializer)

        if "images" in request.data:
            current_images = instance.images.all()

            # Получаем изображения, пришедшие с фронта
            frontend_images = request.data["images"]
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

            # Добавляем новые изображения, которые есть на фронте, но отсутствуют в базе
            new_images_data = request.FILES.getlist("new_images")

            self.create_images(new_images_data, instance)
        updated_instance = self.get_object()

        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_images(self, images_data, post):

        for image_data in images_data:
            PostImage.objects.create(post=post, image=image_data)
        return Response(status=status.HTTP_201_CREATED)
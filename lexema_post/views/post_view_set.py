from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from lexema_post.models import Post, PostImage
from lexema_post.serializers.post_serializer import PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Модель для списка постов"""

    # permission_classes = [IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Post.objects.all().order_by("-created_at")  # pylint: disable=no-member
    serializer_class = PostSerializer

    def get_queryset(self):
        author_id = self.request.query_params.get("author")
        if author_id:
            return Post.objects.filter(  # pylint: disable=no-member
                author=author_id
            ).order_by("-created_at")
        else:
            return Post.objects.none()  # pylint: disable=no-member

    def create(self, request, *args, **kwargs):
        post_data = request.data

        images_data = request.FILES.getlist("images")

        post_serializer = self.get_serializer(data=post_data)
        post_serializer.is_valid(raise_exception=True)
        post = post_serializer.save()

        for image_data in images_data:
            PostImage.objects.create(  # pylint: disable=no-member
                post=post, image=image_data
            )
        return Response(post_serializer.data, status=status.HTTP_201_CREATED)

"""Модель для списка постов"""

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

# from rest_framework.permissions import IsAuthenticated
from lexema_app.models.posts.Posts import Posts
from lexema_app.models.posts.PostImage import PostImage
from lexema_app.serializers.post.PostSerializer import PostsSerializer


class PostsViewSet(viewsets.ModelViewSet):
    """Модель для списка постов"""

    # permission_classes = [IsAuthenticated]
    permission_classes = [permissions.AllowAny]
    queryset = Posts.objects.all().order_by("-created_at")  # pylint: disable=no-member
    serializer_class = PostsSerializer

    def get_queryset(self):
        author_id = self.request.query_params.get("author")
        if author_id:
            return Posts.objects.filter(  # pylint: disable=no-member
                author=author_id
            ).order_by("-created_at")
        else:
            return Posts.objects.none()  # pylint: disable=no-member

    def create(self, request, *args, **kwargs):

        post_data = request.data.copy()

        images_data = request.FILES.getlist("images")

        post_serializer = self.get_serializer(data=post_data)
        post_serializer.is_valid(raise_exception=True)
        post = post_serializer.save()

        for image_data in images_data:
            PostImage.objects.create(  # pylint: disable=no-member
                post=post, image=image_data
            )
        return Response(post_serializer.data, status=status.HTTP_201_CREATED)

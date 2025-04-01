from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status, generics
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from lexema_comment.models import Comments, CommentImages
from lexema_comment.serializers import CommentsSerializer, RecursiveRootCommentSerializer, \
     RecursiveChildCommentsSerializer


# Create your views here.
class RootCommentsView(ListAPIView):
    queryset = Comments.objects.filter(parent=None)
    serializer_class = RecursiveRootCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination


    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comments.objects.filter(post=post_id, parent=None)

class ChildCommentsView(generics.GenericAPIView):
    serializer_class = RecursiveChildCommentsSerializer
    permission_classes = [IsAuthenticated]


    def get(self, request, post_id, parent_id):

        try:
            root_comment = Comments.objects.get(id=parent_id, post_id=post_id)
        except Comments.DoesNotExist:
            return Response({"error": _("Корневой комментарий не найден")}, status=status.HTTP_404_NOT_FOUND)

        child_comments = root_comment.replies.all()

        serializer = RecursiveChildCommentsSerializer(child_comments,many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination


    def get_queryset(self):
        return Comments.objects.all()

    def perform_create(self, serializer):
        post_id = self.request.data.get('post_id')
        parent_id = self.request.data.get('parent_id')
        serializer.save(author=self.request.user, post_id=post_id, parent_id=parent_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        images_data = request.FILES.getlist('images')
        self.perform_create(serializer)
        self.create_image(images_data, serializer.instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if "new_images" in request.data:
            new_images_data = request.FILES.getlist("new_images")
            self.create_image(new_images_data, instance)

        updated_instance = self.get_object()

        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data)

    @staticmethod
    def create_image(images_data, comment):
        for image_data in images_data:
            CommentImages.objects.create(comment=comment, image=image_data)
        return Response(status=status.HTTP_201_CREATED)
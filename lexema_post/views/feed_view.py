from django.db.models import OuterRef, Subquery
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from lexema_friends.models import Friends
from lexema_group.models import GroupMembership
from lexema_post.models import Post
from lexema_post.serializers.post_serializer import PostSerializer


class FeedView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user = request.user

        user_groups = GroupMembership.objects.filter(  # pylint: disable=no-member
            user=user
        ).values_list("group", flat=True)
        group_posts = Post.objects.filter(  # pylint: disable=no-member
            group__in=user_groups
        ).order_by("-created_at")[:10]

        friends = Friends.objects.filter(  # pylint: disable=no-member
            user=user, status="accepted"
        ).values_list("friend", flat=True)

        latest_posts = (
            Post.objects.filter(author=OuterRef("author"))  # pylint: disable=no-member
            .order_by("-created_at")
            .values("id")[:10]
        )

        friends_posts = Post.objects.filter(  # pylint: disable=no-member
            id__in=Subquery(latest_posts), author__in=friends
        ).order_by("-created_at")

        posts = (group_posts | friends_posts).distinct().order_by("-created_at")

        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)

        serializer = PostSerializer(paginated_posts, many=True)

        response = paginator.get_paginated_response(serializer.data)

        return response

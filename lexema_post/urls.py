from django.urls import include, path
from rest_framework import routers

from lexema_post.views import PostViewSet, MainFeedView, RepostRetrieveView

router = routers.DefaultRouter()
router.register(r'profile/(?P<user_id>\d+)/posts', PostViewSet, basename='user-posts')
router.register(r'group/(?P<group_id>\d+)/posts', PostViewSet, basename='group-posts')
router.register(r'friend/(?P<friend_id>\d+)/posts', PostViewSet, basename='friend-posts')

urlpatterns = [
    path("feed/", MainFeedView.as_view(), name="main-feed"),
    path('repost/<int:post_id>/', RepostRetrieveView.as_view(), name="repost"),
    path("", include(router.urls)),
]

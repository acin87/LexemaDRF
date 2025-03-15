from django.urls import include, path
from rest_framework import routers

from lexema_post.views.feed_view import FeedView
from lexema_post.views.post_view_set import PostViewSet


router = routers.DefaultRouter()
router.register(r"posts", PostViewSet)

urlpatterns = [
    path("feed/", FeedView.as_view(), name="feed"),
    path("", include(router.urls)),
]

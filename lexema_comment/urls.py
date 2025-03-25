from django.urls import path, include
from rest_framework import routers

from lexema_comment.views import RootCommentsView, CommentViewSet, ChildCommentsView

router = routers.DefaultRouter()

router.register(r"comments", CommentViewSet)

urlpatterns = [
    path("root_comments/<int:post_id>/", RootCommentsView.as_view(), name="root-comments"),
    path("child_comments/<int:post_id>/<int:parent_id>/", ChildCommentsView.as_view(), name="child-comments"),
    path("", include(router.urls)),
]
from rest_framework import routers

from lexema_post.views.post_view_set import PostViewSet


router = routers.DefaultRouter()
router.register(r"posts", PostViewSet)

urlpatterns = router.urls

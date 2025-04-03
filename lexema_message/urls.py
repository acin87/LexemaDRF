from django.urls import include, path
from rest_framework import routers

from lexema_message.views import MessageViewSet, LatestMessageViewSet

router = routers.DefaultRouter()
router.register(r"message", MessageViewSet, basename="message")
router.register(r"message-latest", LatestMessageViewSet, basename="latest-message")


urlpatterns = [
    path("", include(router.urls)),
]

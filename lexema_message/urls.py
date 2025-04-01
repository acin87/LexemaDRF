from django.urls import include, path
from rest_framework import routers

from lexema_message.views import MessageViewSet


router = routers.DefaultRouter()
router.register(r"message", MessageViewSet)


urlpatterns = [
    path("", include(router.urls)),
]

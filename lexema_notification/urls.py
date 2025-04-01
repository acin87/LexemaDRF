from django.urls import path, include
from rest_framework import routers

from lexema_notification.views import NotificationViewSet

router = routers.DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path("", include(router.urls)),
]
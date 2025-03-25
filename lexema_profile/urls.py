from django.urls import include, path
from rest_framework import routers


from lexema_profile.views import ProfileViewSet

router = routers.DefaultRouter()
router.register(r"profile", ProfileViewSet, basename="profile")
urlpatterns = [
    path("", include(router.urls)),
]

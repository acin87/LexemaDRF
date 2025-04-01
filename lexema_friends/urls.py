from django.urls import path, include
from rest_framework import routers

from lexema_friends.views import FriendsViewSet, UpcomingBirthDayFriendsView



router = routers.DefaultRouter()
router.register(r"friends", FriendsViewSet, basename="friends")
urlpatterns = [
    path("upcoming-birth-day/", UpcomingBirthDayFriendsView.as_view(), name="upcoming-birth-day"),
    path("", include(router.urls)),
]

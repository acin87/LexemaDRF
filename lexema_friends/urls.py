from django.urls import path, include
from rest_framework import routers

from lexema_friends.views import FriendsView, UpcomingBirthDayFriendsView

urlpatterns = [
    path("friends/", FriendsView.as_view(), name="friends"),
    path("upcoming-birth-day/", UpcomingBirthDayFriendsView.as_view(), name="upcoming-birth-day")
]

from django.urls import path, include
from rest_framework import routers

from lexema_friends.views import FriendsView



urlpatterns = [
    path("friends/", FriendsView.as_view(), name="friends"),
]

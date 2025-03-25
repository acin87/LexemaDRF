from django.urls import path, include

from lexema_user.views import UserView, UserById

urlpatterns = [
    path('me/', UserView.as_view(), name='user'),
]
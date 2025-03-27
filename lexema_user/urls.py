from django.urls import path, include

from lexema_user.views import UserView, UserAutocompleteView

urlpatterns = [
    path('me/', UserView.as_view(), name='user'),
    path('users/autocomplete/', UserAutocompleteView.as_view(), name='user-autocomplete'),
]
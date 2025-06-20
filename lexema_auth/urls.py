from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from lexema_auth.views import RegisterView, CustomTokenObtainPairView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),
]

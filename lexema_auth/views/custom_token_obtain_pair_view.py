from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from lexema_auth.serializers.custom_token_obtain_pair_serializer import (
    CustomTokenObtainPairSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный класс для получения токена"""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_401_UNAUTHORIZED)

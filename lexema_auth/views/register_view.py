from rest_framework import generics, permissions
from rest_framework.response import Response

from lexema_auth.serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """View для регистрации пользователя"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": RegisterSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": "Пользователь успешно создан.",
            }
        )

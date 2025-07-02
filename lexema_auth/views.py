from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from lexema_auth.serializers import CustomTokenObtainPairSerializer, RegisterSerializer
from lexema_profile.models import Profile, ProfileImages


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомный класс для получения токена"""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(generics.CreateAPIView):
    """View для регистрации пользователя"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            profile = Profile.objects.create(user=user)
            profile.save()
            profile_images = ProfileImages.objects.create(profile=profile)
            profile_images.main_page_image = "users/images/default_profile_image.webp"
            profile_images.save()

        return Response(
            {
                "user": RegisterSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "message": _("Пользователь успешно создан."),
            }
        )

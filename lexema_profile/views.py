from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lexema_profile.models import Profile
from lexema_profile.serializers import (
    ProfileSerializer,
)


# Create your views here.
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.filter(user=self.kwargs.get("pk"))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": f"Профиль с id-{self.kwargs.get("pk")} не найден."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_queryset().first()
        if instance:
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                if request.data.get("first_name"):
                    instance.user.first_name = request.data.get("first_name")
                    instance.user.save()
                if request.data.get("last_name"):
                    instance.user.last_name = request.data.get("last_name")
                    instance.user.save()
                avatar = request.FILES.get("avatar")
                if avatar:
                    instance.images.avatar_image = avatar
                    instance.images.save()
                profile_image = request.FILES.get("profile_image")
                if profile_image:
                    instance.images.main_page_image = profile_image
                    instance.images.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": f"Профиль с id-{self.kwargs.get("pk")} не найден."},
            status=status.HTTP_400_BAD_REQUEST,
        )

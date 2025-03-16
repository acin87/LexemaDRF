from django.shortcuts import render
from rest_framework import viewsets

from lexema_profile.models import Profile
from lexema_profile.profile_serializers import ProfileSerializer


# Create your views here.
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)
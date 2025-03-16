from django.shortcuts import render

from django.views.generic import ListView
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lexema_friends.models import Friends
from lexema_friends.serializers.friends_serializers import FriendsSerializer


# Create your views here.
class FriendsView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer

    def get(self, request):
        user = request.user
        friends = Friends.objects.filter(user=user, status="accepted")
        serializer = FriendsSerializer(friends, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
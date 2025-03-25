from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lexema_friends.models import Friends
from lexema_friends.serializers import (
    FriendsSerializer,
    UpcomingBirthDayFriendsSerializer,
)


# Create your views here.
class FriendsView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Friends.objects.all()
    serializer_class = FriendsSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request):
        user = request.user

        friends = Friends.objects.filter(user=user, status="accepted").select_related(
            "friend__profile"
        )
        paginator = self.pagination_class()

        paginator_friends = paginator.paginate_queryset(friends, request)

        serializer = FriendsSerializer(paginator_friends, many=True)

        response = paginator.get_paginated_response(serializer.data)

        return Response(response.data, status=status.HTTP_200_OK)


class UpcomingBirthDayFriendsView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Friends.objects.all()
    serializer_class = UpcomingBirthDayFriendsSerializer

    @staticmethod
    def get(request):
        user = request.user
        today = datetime.now().date()
        end_date = today + timedelta(days=5)
        friends = Friends.objects.filter(user=user, status="accepted").select_related(
            "friend__profile"
        )
        friends = friends.filter(
            friend__profile__birth_date__month__in=[today.month, end_date.month],
            friend__profile__birth_date__day__gte=today.day,
            friend__profile__birth_date__day__lte=end_date.day,
        )[:2]

        serializer = UpcomingBirthDayFriendsSerializer(friends, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lexema_user.models import User
from lexema_user.serializers import UserSerializerWithAvatar


# Create your views here.
class UserView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializerWithAvatar
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializerWithAvatar(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserById(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializerWithAvatar
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.get(id=self.kwargs['pk'])




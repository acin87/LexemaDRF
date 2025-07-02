from django.db.models import Q
from rest_framework import status, generics
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from lexema_user.models import User
from lexema_user.serializers import UserSerializerWithAvatar, UserAutocompleteSerializer


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
        return self.queryset.get(id=self.kwargs["pk"])


# views.py
class UserAutocompleteView(generics.ListAPIView):
    serializer_class = UserAutocompleteSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()
        if not query or len(query) < 2:
            return User.objects.none()

        # Разбиваем запрос на слова
        terms = query.split()
        q_objects = Q()

        # Для каждого слова ищем в имени и фамилии
        for term in terms:
            q_objects &= (
                Q(username__istartswith=term)
                | Q(first_name__istartswith=term)
                | Q(last_name__istartswith=term)
                | Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
            )

        return (
            User.objects.filter(q_objects)
            .order_by("first_name", "last_name")
            .exclude(id=self.request.user.id)[:10]
        )

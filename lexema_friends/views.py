from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from lexema_friends.models import Friend
from lexema_friends.serializers import (
    FriendsSerializer,
    UpcomingBirthDayFriendsSerializer,
)


# Create your views here.
class FriendsViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated]
    queryset = Friend.objects.all()

    serializer_class = FriendsSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return self.queryset.filter(
            Q(user=self.request.user) | Q(friend=self.request.user)
        )

    def list(self, request, *args, **kwargs):
        user = request.user
        # Получаем все подтвержденные дружеские связи, где пользователь участвует
        friendships = Friend.objects.filter(
            Q(user=user) | Q(friend=user), status="accepted"
        ).select_related("user__profile__images", "friend__profile__images")

        # Собираем уникальных друзей
        friends_data = []
        seen_user_ids = set()

        for friendship in friendships:
            # Определяем, кто является другом (не текущий пользователь)
            if friendship.user == user:
                friend_user = friendship.friend
                friendship_creator = False  # Дружбу создал текущий пользователь
            else:
                friend_user = friendship.user
                friendship_creator = True  # Дружбу создал другой пользователь

            # Пропускаем дубликаты
            if friend_user.id in seen_user_ids:
                continue

            seen_user_ids.add(friend_user.id)

            # Создаем временный объект Friend с нужными данными
            temp_friend = Friend(
                id=friendship.id,
                user=user,  # Всегда текущий пользователь
                friend=friend_user,
                status="accepted",
                created_at=friendship.created_at,
                updated_at=friendship.updated_at,
            )
            # Добавляем флаг, кто инициировал дружбу
            temp_friend.friendship_creator = friendship_creator

            friends_data.append(temp_friend)

        serializer = self.get_serializer(friends_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        friend = request.data["friend_id"]
        if user == friend:
            raise ValidationError(_("Нельзя добавить себя в друзья"))
        if Friend.objects.filter(user=user, friend_id=friend).exists():
            raise ValidationError(_("Заявка уже отправлена"))
        Friend.objects.create(user=user, friend_id=friend, status="pending")
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="mutual_friends")
    def mutual(self, request, pk=None):
        """Список друзей пользователя с отметкой общих друзей"""
        current_user = request.user
        target_user = get_object_or_404(get_user_model(), pk=pk)

        # Получаем всех друзей целевого пользователя (кроме текущего)
        target_friends = (
            Friend.objects.filter(
                (Q(user=target_user) | Q(friend=target_user)), status="accepted"
            )
            .exclude(Q(user=current_user) | Q(friend=current_user))
            .select_related("user__profile__images", "friend__profile__images")
        )

        friends_data = []
        seen_users = set()

        for friendship in target_friends:

            friend_user = (
                friendship.friend if friendship.user == target_user else friendship.user
            )

            if friend_user.id in seen_users:
                continue

            seen_users.add(friend_user.id)

            temp_friend = Friend(
                id=friendship.id,
                user=target_user,
                friend=friend_user,
                status="accepted",
                created_at=friendship.created_at,
                updated_at=friendship.updated_at,
            )
            friends_data.append(temp_friend)

        # Сериализуем с флагом mutual_mode
        serializer = self.get_serializer(
            friends_data,
            many=True,
            context={
                "request": request,
                "mutual_mode": True,  # Включаем режим отображения isMutual
            },
        )

        # Подсчет общих друзей

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        try:
            friendship = self.get_object()
            print(friendship)
            new_status = request.data.get("status")
            print(new_status)
            # Проверяем, что текущий пользователь - получатель запроса
            if friendship.friend != request.user:
                return Response(
                    {"error": _("Вы можете отвечать только на свои запросы")},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Обновляем статус
            friendship.status = new_status
            friendship.save()

            return Response(FriendsSerializer(friendship).data)

        except Friend.DoesNotExist:
            return Response(
                {"error": _("Запрос на дружбу не найден")},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"])
    def remove_friend(self, request, pk=None):
        try:
            friendship = self.get_object()

            # Проверяем, что пользователь участвует в дружбе
            if request.user not in [friendship.user, friendship.friend]:
                return Response(
                    {"error": _("Вы не можете удалить эту дружбу")},
                    status=status.HTTP_403_FORBIDDEN,
                )

            friendship.remove_friendship(initiator=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Friend.DoesNotExist:
            return Response(
                {"error": _("Запись о дружбе не найдена")},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"])
    def cancel_request(self, request, pk=None):
        """Отмена запроса на дружбу (для отправителя). Удаление из друзей (для обеих сторон)"""
        try:
            friendship = Friend.objects.get(
                Q(id=pk) & (Q(user=request.user) | Q(friend=request.user))
            )
            # Если пользователь - отправитель запроса (может отменить pending)
            if (
                friendship.user == request.user
                and friendship.status == Friend.Status.PENDING
            ):
                friendship.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            # Если пользователь - получатель (может удалить запрос, даже если accepted)
            elif friendship.friend == request.user:
                friendship.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            else:
                return Response(
                    {
                        "error": _(
                            "Вы можете отменить только свои запросы в статусе 'pending'"
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Friend.DoesNotExist:
            return Response(
                {"error": _("Запись о дружбе не найдена или у вас нет прав")},
                status=status.HTTP_404_NOT_FOUND,
            )


class UpcomingBirthDayFriendsView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Friend.objects.all()
    serializer_class = UpcomingBirthDayFriendsSerializer

    @staticmethod
    def get(request):
        user = request.user
        today = datetime.now().date()
        end_date = today + timedelta(days=5)
        friends = Friend.objects.filter(user=user, status="accepted").select_related(
            "friend__profile"
        )
        friends = friends.filter(
            friend__profile__birth_date__month__in=[today.month, end_date.month],
            friend__profile__birth_date__day__gte=today.day,
            friend__profile__birth_date__day__lte=end_date.day,
        )[:2]

        serializer = UpcomingBirthDayFriendsSerializer(friends, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

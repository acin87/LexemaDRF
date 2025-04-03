from django.db.models import Q, Max
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from lexema_message.models import Message
from lexema_message.serializers import FullMessageSerializer, ShortMessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = FullMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ShortMessageSerializer
        return FullMessageSerializer

    def get_queryset(self):

        return (
            self.queryset.filter(
                Q(sender=self.request.user) | Q(recipient=self.request.user)
            )
            .select_related("sender", "recipient")
            .order_by("-timestamp")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        if message.recipient == request.user:
            message.mark_as_read()  # Помечает сообщение и уведомления
            return Response({"status": "Сообщение помечено как прочитанное"})
        return Response(
            {"error": "Вы не получатель этого сообщения"},
            status=status.HTTP_403_FORBIDDEN,
        )


class LatestMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = ShortMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Получаем максимальные timestamp для каждого отправителя, где текущий пользователь - получатель
        latest_messages = (
            Message.objects.filter(recipient=self.request.user, is_read=False)
            .values("sender")
            .annotate(last_timestamp=Max("timestamp"))
        )

        # Получаем список ID последних сообщений
        latest_message_ids = Message.objects.filter(
            recipient=self.request.user,
            timestamp__in=[item["last_timestamp"] for item in latest_messages],
        ).values_list("id", flat=True)

        return (
            Message.objects.filter(id__in=latest_message_ids)
            .select_related("sender", "recipient")
            .order_by("-timestamp")
        )

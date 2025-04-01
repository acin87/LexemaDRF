from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from lexema_message.models import Message
from lexema_message.serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            self.queryset.filter(
                Q(sender=self.request.user) | Q(recipient=self.request.user)
            )
            .select_related("sender", "recipient")
            .order_by("-timestamp")
        )

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

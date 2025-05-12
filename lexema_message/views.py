from django.db import models
from django.db.models import Q, Max, OuterRef, Subquery, When, Case, F
from django.db.models.fields import return_None
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from lexema_message.models import Message
from lexema_message.serializers import FullMessageSerializer, ShortMessageSerializer
from lexema_notification.models import Notification, NotificationType


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = FullMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return ShortMessageSerializer
        return FullMessageSerializer

    def get_queryset(self):
        queryset = (
            self.queryset.filter(
                Q(sender=self.request.user) | Q(recipient=self.request.user)
            )
            .select_related("sender", "recipient")
            .order_by("timestamp")
        )

        return queryset

    def list(self, request, *args, **kwargs):
        sender_id = request.GET.get("sender_id")

        queryset = self.get_queryset().filter(
            Q(sender_id=sender_id) | Q(recipient_id=sender_id)
        )

        serializer = self.get_serializer(queryset, many=True)
        print(serializer.data)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def send_message(self, request, *args, **kwargs):
        print(request.data)
        request.data["recipient"] = request.data.get("recipient_id")
        request.data["sender"] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user)
        return Response(self.get_serializer(message).data)

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

    @action(detail=False, methods=["post"])
    def mark_as_read_all_messages(self, request, *args, **kwargs):
        sender_id = request.data.get("sender_id")
        if request.user.pk == request.data.get("sender_id"):
            return None
        queryset = Message.objects.filter(
            Q(recipient_id=sender_id, sender=request.user)
            | Q(sender_id=sender_id, recipient=request.user),
        )
        if queryset.exists():
            queryset.update(is_read=True)

            Notification.objects.filter(
                recipient=request.user,
                sender_id=sender_id,
                notification_type=NotificationType.NEW_MESSAGE,
            ).update(is_read=True)

            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"])
    def delete_all_messages(self, request, *args, **kwargs):
        recipient_id = request.data.get("recipient_id")
        if request.user.pk == request.data.get("recipient_id"):
            return None

        queryset = Message.objects.filter(
            Q(recipient_id=recipient_id, sender=request.user)
            | Q(sender_id=recipient_id, recipient=request.user)
        )
        if queryset.exists():
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


class LatestMessageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = ShortMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == "list":
            user = self.request.user
            other_users = (
                Message.objects.filter(Q(sender=user) | Q(recipient=user))
                .annotate(
                    other_user=Case(
                        When(sender=user, then=F("recipient")),
                        When(recipient=user, then=F("sender")),
                        output_field=models.IntegerField(),
                    )
                )
                .values("other_user")
                .distinct()
            )

            latest_ids = []
            for other in other_users:
                last_msg = (
                    Message.objects.filter(
                        Q(sender=user, recipient=other["other_user"])
                        | Q(sender=other["other_user"], recipient=user)
                    )
                    .order_by("-timestamp")
                    .values("id")[:1]
                )
                latest_ids.append(last_msg[0]["id"])

            queryset = Message.objects.filter(id__in=latest_ids).order_by("-timestamp")

            return queryset

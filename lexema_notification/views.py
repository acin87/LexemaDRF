from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from lexema_notification.models import Notification
from lexema_notification.serializers import NotificationSerializer


class NotificationsPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50
    template = None


# Create your views here.
class NotificationViewSet(
    GenericViewSet, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    # pagination_class = NotificationsPagination
    lookup_field = "pk"

    def get_queryset(self):
        """Возвращает только уведомления текущего пользователя с оптимизацией"""
        return (
            Notification.objects.filter(recipient=self.request.user)
            .select_related("sender")
            .order_by("-created_at")
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Только непрочитанные уведомления"""
        queryset = self.filter_queryset(self.get_queryset().filter(is_read=False))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """Пометить все как прочитанные"""
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"marked": updated})

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        """Пометить конкретное уведомление как прочитанное"""
        notification = self.get_object()
        print(notification)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data)

    def list(self, request, *args, **kwargs):
        """Основной список с дополнительной статистикой"""
        response = super().list(request, *args, **kwargs)
        response.data["unread_count"] = (
            self.get_queryset().filter(is_read=False).count()
        )
        return response

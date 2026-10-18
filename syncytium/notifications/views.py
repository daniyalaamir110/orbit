from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.paginators import CustomLimitOffsetPagination

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(ListModelMixin, GenericViewSet):
    """List the current user's notifications, with unread count and read actions."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        return (
            Notification.objects.filter(recipient=self.request.user)
            .select_related("actor", "post")
        )

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread": count})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        updated = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({"marked_read": updated}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response(self.get_serializer(notification).data)

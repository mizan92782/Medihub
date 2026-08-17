from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from notification.models.app_notification_mod import AppNotification
from notification.serializers import AppNotificationSerializer
from core.decorators import api_exception_handler
from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AppNotificationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return AppNotification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'])
    @api_exception_handler
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response(
            APIResponse.success(message="Unread notification count retrieved successfully", title="unread_count", data=count),
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    @api_exception_handler
    def mark_all_read(self, request):
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response(
            APIResponse.success(message="All notifications marked as read"),
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    @api_exception_handler
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(
            APIResponse.success(message="Notification marked as read", title="notification", data=self.get_serializer(notification).data),
            status=status.HTTP_200_OK
        )
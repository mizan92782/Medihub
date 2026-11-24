from rest_framework import serializers
from notification.models.app_notification_mod import AppNotification
from authentication.models import User


class AppNotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AppNotification
        fields = [
            "id", "user", "category", "priority", "title", "message",
            "is_read", "action_url", "action_label", "post_id", "post_type", "created_at"
        ]
        read_only_fields = ["id", "user", "created_at"]
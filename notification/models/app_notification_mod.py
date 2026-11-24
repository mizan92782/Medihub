from django.db import models
from authentication.models import User 


class NotificationCategoryChoices(models.TextChoices):
    EMERGENCY = "emergency", "Emergency (Blood/Ambulance)"
    APPOINTMENT = "appointment", "Doctor Appointment"
    MEDICAL_ORDER = "medical_order", "Lab Test & Pharmacy"
    QA_MESSAGE = "qa_message", "Q&A & Message"
    SOCIAL = "social", "Social & Blog"


class NotificationPriorityChoices(models.TextChoices):
    URGENT = "urgent", "Urgent"
    HIGH = "high", "High"
    NORMAL = "normal", "Normal"
    LOW = "low", "Low"


'''AppNotification: store app notification in database for rich user engagement'''
class AppNotification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='app_notification'
    )
    category = models.CharField(
        max_length=20,
        choices=NotificationCategoryChoices.choices,
        default=NotificationCategoryChoices.SOCIAL,
        db_index=True
    )
    priority = models.CharField(
        max_length=15,
        choices=NotificationPriorityChoices.choices,
        default=NotificationPriorityChoices.NORMAL,
        db_index=True
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)

    # Actionable deep linking for high user engagement
    action_url = models.CharField(max_length=500, blank=True, null=True)
    action_label = models.CharField(max_length=60, blank=True, null=True)

    post_id = models.PositiveIntegerField(null=True, blank=True)
    post_type = models.CharField(max_length=30, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"], name="appnotif_user_read_idx"),
            models.Index(fields=["user", "category"], name="appnotif_user_cat_idx"),
            models.Index(fields=["created_at"], name="appnotif_created_idx"),
        ]

    def __str__(self):
        return f"[{self.category}] {self.title}"
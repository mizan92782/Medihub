from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def notify_ambulance_owner_on_review(self, ambulance_id, reviewer_email, rating):
    try:
        from profiles.models import AmbulanceProfile
        from notification.servcies import AppNotificationService, PushNotification

        ambulance = AmbulanceProfile.objects.select_related('user').get(pk=ambulance_id)
        owner = ambulance.user

        title = "New Review Received"
        message = f"{reviewer_email} gave your ambulance ({ambulance.vehicle_number}) a {rating}★ rating."

        AppNotificationService.create_notification(
            user=owner,
            title=title,
            message=message,
            post_type="ambulance_review",
            post_id=ambulance_id,
        )

        PushNotification.send_to_user(user=owner, title=title, body=message)

    except Exception as exc:
        logger.exception("notify_ambulance_owner_on_review failed")
        raise self.retry(exc=exc)

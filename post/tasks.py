from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10, queue='default')
def send_urgent_blood_notifications(self, post_id):
    """
    Background task: notify all available donors matching blood group + district
    of an urgent blood post. Runs via RabbitMQ → Celery worker.
    """
    try:
        from post.models.blood_need_mod import BloodNeedPost
        from profiles.models.blood_donor_mod import BloodDonor
        from notification.servcies import AppNotificationService, PushNotification

        post = BloodNeedPost.objects.select_related('district').get(id=post_id)

        if not post.district:
            logger.warning(f'urgent_blood_notify: post {post_id} has no district, skipping')
            return 'skipped: no district'

        donors = BloodDonor.objects.filter(
            blood_group=post.blood_group,
            district=post.district,
            availability='available'
        ).select_related('user')

        title = f'🚨 Urgent Blood Needed: {post.blood_group}'
        message = (
            f'{post.bags_needed} bag(s) of {post.blood_group} needed for {post.patient_name} '
            f'at {post.hospital_name}, {post.district.district_name_eng}. '
            f'Contact: {post.contact_number}'
        )

        notified = 0
        for donor in donors:
            AppNotificationService.create_notification(
                user=donor.user,
                title=title,
                message=message,
                post_id=post.id,
                post_type='blood_need'
            )
            PushNotification.send_to_user(user=donor.user, title=title, body=message)
            notified += 1
            logger.info(f'urgent_blood_notify: notified {donor.user.email} for post {post_id}')

        logger.info(f'urgent_blood_notify: post {post_id} → {notified} donors notified')
        return f'notified {notified} donors'

    except Exception as exc:
        logger.error(f'urgent_blood_notify: failed for post {post_id} — {exc}')
        raise self.retry(exc=exc)

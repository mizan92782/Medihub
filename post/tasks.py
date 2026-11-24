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


@shared_task(bind=True, max_retries=2, default_retry_delay=10, queue='default')
def notify_followers_new_post_task(self, author_id, post_type, post_id, summary):
    """
    Background task: dispatch notifications to all followers of an author when a post is created.
    Runs asynchronously via Celery worker to keep HTTP request response fast.
    """
    try:
        from authentication.models import User
        from interactions.models.user_follow import UserFollow
        from notification.servcies import AppNotificationService, PushNotification

        author = User.objects.filter(id=author_id).first()
        if not author:
            return 'skipped: author not found'

        followers = UserFollow.objects.filter(following=author).select_related('follower')
        author_name = author.email.split('@')[0]
        try:
            if hasattr(author, 'doctor') and author.doctor:
                d = author.doctor
                author_name = f"Dr. {d.first_name} {d.last_name}".strip() or author_name
            elif hasattr(author, 'profile') and author.profile:
                p = author.profile
                author_name = f"{p.first_name} {p.last_name}".strip() or author_name
            elif hasattr(author, 'blood_donor') and author.blood_donor:
                d = author.blood_donor
                author_name = f"{d.first_name} {d.last_name}".strip() or author_name
        except Exception:
            pass

        title = f"{author_name} posted something new"
        message = f"{author_name}: {summary}"
        for follow in followers:
            AppNotificationService.create_notification(
                user=follow.follower,
                title=title,
                message=message,
                post_id=post_id,
                post_type=post_type,
            )
            PushNotification.send_to_user(follow.follower, title, message)
        return f"notified {followers.count()} followers"
    except Exception as exc:
        logger.error(f'notify_followers_task failed for author {author_id}: {exc}')
        raise self.retry(exc=exc)

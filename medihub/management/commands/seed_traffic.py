import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from authentication.models import User


class Command(BaseCommand):
    help = 'Seed realistic backdated user registration data for the last 12 months to populate traffic charts'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        created_dates = []

        # Monthly growth pattern: ramp up over 12 months
        monthly_counts = [4, 6, 8, 10, 14, 18, 22, 28, 35, 42, 50, 60]

        for month_offset, count in enumerate(monthly_counts):
            month_start = now - timedelta(days=(12 - month_offset) * 30)
            for _ in range(count):
                # Random day within that month
                day_offset = random.randint(0, 29)
                hour = random.randint(6, 23)
                minute = random.randint(0, 59)
                created_at = month_start + timedelta(days=day_offset, hours=hour, minutes=minute)
                created_dates.append(created_at)

        # Also add daily variation for the last 30 days
        for day_offset in range(30):
            day = now - timedelta(days=30 - day_offset)
            daily_count = random.randint(1, 8)
            for _ in range(daily_count):
                hour = random.randint(6, 23)
                created_at = day.replace(hour=hour, minute=random.randint(0, 59), second=0, microsecond=0)
                created_dates.append(created_at)

        user_types = ['regular', 'doctor', 'blood_donor', 'ambulance', 'pharmacy', 'diagnostic']
        weights     = [50, 20, 15, 5, 5, 5]

        created_count = 0
        for i, created_at in enumerate(created_dates):
            user_type = random.choices(user_types, weights=weights)[0]
            email = f'seed_traffic_{i}_{int(created_at.timestamp())}@medihub.test'

            if User.objects.filter(email=email).exists():
                continue

            user = User(
                email=email,
                user_type=user_type,
                is_active=True,
            )
            user.set_unusable_password()
            user.save()

            # Backdate the created field directly via SQL to bypass auto_now_add
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE authentication_user SET created = %s WHERE id = %s",
                    [created_at, user.id]
                )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_count} backdated users across the last 12 months.'
        ))

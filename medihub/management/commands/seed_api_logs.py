import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import connection
from authentication.models import User
from medihub.models import APIRequestLog

ENDPOINTS = [
    ('GET',  '/doctors/'),
    ('GET',  '/donors/'),
    ('GET',  '/ambulances/'),
    ('GET',  '/diagnostics/'),
    ('GET',  '/pharmacies/'),
    ('GET',  '/blogs/posts/'),
    ('GET',  '/posts/blood-need/'),
    ('POST', '/authentication/auth/login/'),
    ('GET',  '/profiles/doctors/me/'),
    ('GET',  '/notification/app/'),
    ('GET',  '/api/admin/traffic/'),
    ('GET',  '/feed/'),
]

STATUS_WEIGHTS = [200] * 85 + [201] * 5 + [400] * 5 + [401] * 3 + [404] * 2
ANON_IPS = [f'10.0.{i}.{j}' for i in range(1, 5) for j in range(1, 6)]


class Command(BaseCommand):
    help = 'Seed API logs with visitor data'

    def handle(self, *args, **kwargs):
        users_by_type = {}
        for u in User.objects.only('id', 'user_type'):
            users_by_type.setdefault(u.user_type, []).append(u.id)

        if not users_by_type:
            self.stdout.write(self.style.ERROR('No users found.'))
            return

        all_ids = [uid for ids in users_by_type.values() for uid in ids]
        now = timezone.now()

        # small counts — fast to insert and backdate
        monthly_base = [30, 40, 50, 60, 80, 100, 120, 150, 180, 200, 220, 250]

        rows = []
        for month_offset, base_count in enumerate(monthly_base):
            month_start = now - timedelta(days=(12 - month_offset) * 30)
            for _ in range(base_count):
                ts = month_start + timedelta(
                    days=random.randint(0, 29),
                    hours=random.randint(6, 22),
                    minutes=random.randint(0, 59),
                )
                method, path = random.choice(ENDPOINTS)
                status = random.choice(STATUS_WEIGHTS)
                if random.random() < 0.30:
                    uid, ip = None, random.choice(ANON_IPS)
                else:
                    utype = random.choices(
                        ['doctor', 'blood_donor', 'ambulance', 'pharmacy', 'diagnostic', 'regular'],
                        weights=[20, 25, 10, 10, 10, 25],
                    )[0]
                    uid = random.choice(users_by_type.get(utype) or all_ids)
                    ip = None
                rows.append((path, method, status, ts, uid, ip))

        total = len(rows)
        self.stdout.write(f'Inserting {total} logs...')

        objs = [
            APIRequestLog(path=p, method=m, status_code=s, user_id=uid, ip=ip)
            for p, m, s, _, uid, ip in rows
        ]
        created = APIRequestLog.objects.bulk_create(objs, batch_size=500)
        start_id = created[0].id

        self.stdout.write('Backdating...')

        # single UPDATE using a VALUES join — fastest possible approach
        values_sql = ', '.join(
            f"({start_id + i}, '{ts.strftime('%Y-%m-%d %H:%M:%S')}')"
            for i, (_, _, _, ts, _, _) in enumerate(rows)
        )
        with connection.cursor() as cursor:
            cursor.execute(f"""
                UPDATE medihub_apirequestlog AS t
                SET created = v.ts::timestamptz
                FROM (VALUES {values_sql}) AS v(id, ts)
                WHERE t.id = v.id::int
            """)

        self.stdout.write(self.style.SUCCESS(f'Done! Seeded {total} logs.'))

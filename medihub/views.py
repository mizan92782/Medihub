import os
import json
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.permissions import IsAdminUser
from core.api_response import APIResponse
from authentication.models import User
from profiles.models import (
    Doctor, RegularUserProfile, BloodDonor, AmbulanceProfile,
    PharmacyProfile, DiagnosticProfile, DoctorBooking
)
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.general_post_mod import GeneralPost
from blog.models import BlogPost
from medihub.models import APIRequestLog
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.conf import settings


class AdminUserListView(APIView):
    """
    GET  /admin/users/?type=doctor&page=1&search=
    PATCH /admin/users/<id>/  { is_active: true/false }
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        user_type = request.query_params.get('type', '')
        search = request.query_params.get('search', '')
        page = int(request.query_params.get('page', 1))
        page_size = 20

        qs = User.objects.all().order_by('-date_joined') if hasattr(User, 'date_joined') else User.objects.all().order_by('-id')
        if user_type:
            qs = qs.filter(user_type=user_type)
        if search:
            qs = qs.filter(email__icontains=search)

        total = qs.count()
        start = (page - 1) * page_size
        users = qs[start:start + page_size]

        data = []
        for u in users:
            # Get display name from related profile
            name = ''
            try:
                if u.user_type == 'doctor' and hasattr(u, 'doctor'):
                    name = f"{u.doctor.first_name or ''} {u.doctor.last_name or ''}".strip()
                elif u.user_type == 'blood_donor' and hasattr(u, 'blood_donor'):
                    name = f"{u.blood_donor.first_name or ''} {u.blood_donor.last_name or ''}".strip()
                elif u.user_type == 'ambulance' and hasattr(u, 'ambulance'):
                    name = u.ambulance.owner_name or ''
                elif u.user_type == 'pharmacy' and hasattr(u, 'pharmacy'):
                    name = u.pharmacy.pharmacy_name or ''
                elif u.user_type == 'diagnostic' and hasattr(u, 'diagnostic'):
                    name = u.diagnostic.diagnostic_name or ''
                elif hasattr(u, 'profile'):
                    name = f"{u.profile.first_name or ''} {u.profile.last_name or ''}".strip()
            except Exception:
                pass
            data.append({
                'id': u.id,
                'email': u.email,
                'name': name or u.email.split('@')[0],
                'user_type': u.user_type,
                'is_active': u.is_active,
                'is_staff': u.is_staff,
                'last_login': u.last_login.isoformat() if u.last_login else None,
                'last_status_change': u.updated.isoformat() if u.updated else None,
                'joined': u.created.isoformat() if u.created else None,
            })

        return Response(APIResponse.success('Users fetched', 'users', {'results': data, 'total': total, 'page': page, 'page_size': page_size}))

    def patch(self, request, user_id=None):
        if not user_id:
            return Response({'error': 'user_id required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        is_active = request.data.get('is_active')
        if is_active is not None:
            user.is_active = bool(is_active)
            user.save(update_fields=['is_active'])
        return Response(APIResponse.success('User updated', 'user', {'id': user.id, 'is_active': user.is_active}))


class AdminTrafficStatsView(APIView):
    """
    GET /api/admin/traffic/?range=daily|monthly|yearly
    Returns user registrations + API call counts per period.
    """
    permission_classes = [IsAdminUser]

    def _query(self, qs, trunc_fn, field):
        return (
            qs.annotate(period=trunc_fn(field))
            .values('period')
            .annotate(count=Count('id'))
            .order_by('period')
        )

    def get(self, request):
        range_type = request.query_params.get('range', 'monthly')
        from_date  = request.query_params.get('from')   # e.g. 2024-01-01
        to_date    = request.query_params.get('to')     # e.g. 2024-03-31
        now        = timezone.now()

        # Custom date range overrides range_type
        if from_date and to_date:
            try:
                from datetime import datetime
                # Support YYYY, YYYY-MM, or YYYY-MM-DD formats
                def parse_date(s, end=False):
                    if len(s) == 4:  # year only: 2024
                        if end:
                            return timezone.make_aware(datetime(int(s), 12, 31, 23, 59, 59))
                        return timezone.make_aware(datetime(int(s), 1, 1))
                    elif len(s) == 7:  # month: 2024-01
                        y, m = int(s[:4]), int(s[5:7])
                        if end:
                            import calendar
                            last_day = calendar.monthrange(y, m)[1]
                            return timezone.make_aware(datetime(y, m, last_day, 23, 59, 59))
                        return timezone.make_aware(datetime(y, m, 1))
                    else:  # full date: 2024-01-15
                        d = datetime.strptime(s, '%Y-%m-%d')
                        if end:
                            return timezone.make_aware(d.replace(hour=23, minute=59, second=59))
                        return timezone.make_aware(d)
                since    = parse_date(from_date)
                until    = parse_date(to_date, end=True)
                # Choose trunc granularity based on input format
                if len(from_date) == 4:
                    trunc = TruncYear
                    label_fn = lambda d: str(d['period'])[:4]
                elif len(from_date) == 7:
                    trunc = TruncMonth
                    label_fn = lambda d: str(d['period'])[:7]
                else:
                    trunc = TruncDate
                    label_fn = lambda d: str(d['period'])
            except (ValueError, TypeError):
                return Response({'error': 'Invalid date format. Use YYYY, YYYY-MM, or YYYY-MM-DD'}, status=400)
        elif range_type == 'daily':
            since    = now - timedelta(days=30)
            until    = now
            trunc    = TruncDate
            label_fn = lambda d: str(d['period'])
        elif range_type == 'yearly':
            since    = None
            until    = now
            trunc    = TruncYear
            label_fn = lambda d: str(d['period'])[:4]
        else:  # monthly
            since    = now - timedelta(days=365)
            until    = now
            trunc    = TruncMonth
            label_fn = lambda d: str(d['period'])[:7]

        def date_filter(qs, field):
            if since:
                qs = qs.filter(**{f'{field}__gte': since})
            qs = qs.filter(**{f'{field}__lte': until})
            return qs

        try:
            reg_data = self._query(date_filter(User.objects, 'created'), trunc, 'created')
            registrations = [{'label': label_fn(d), 'value': d['count']} for d in reg_data]
        except Exception:
            registrations = []

        # Summary totals
        try:
            total_api    = APIRequestLog.objects.count()
            today_api    = APIRequestLog.objects.filter(created__date=now.date()).count()
            total_users  = User.objects.count()
            new_users_30d = User.objects.filter(created__gte=now - timedelta(days=30)).count()
        except Exception:
            total_api = today_api = total_users = new_users_30d = 0

        # Distinct visitors by user type
        try:
            auth_visitors = (
                date_filter(APIRequestLog.objects, 'created')
                .filter(user__isnull=False)
                .values('user__user_type')
                .annotate(count=Count('user', distinct=True))
            )
            visitor_breakdown = {row['user__user_type']: row['count'] for row in auth_visitors}
            anon_count = (
                date_filter(APIRequestLog.objects, 'created')
                .filter(user__isnull=True)
                .values('ip')
                .distinct()
                .count()
            )
            visitor_breakdown['anonymous'] = anon_count
        except Exception:
            visitor_breakdown = {}

        return Response(APIResponse.success('Traffic stats', 'traffic', {
            'registrations': registrations,
            'visitor_breakdown': visitor_breakdown,
            'summary': {
                'total_api_calls': total_api,
                'api_calls_today': today_api,
                'total_users': total_users,
                'new_users_30d': new_users_30d,
            }
        }))


class PublicStatsView(APIView):
    permission_classes = []

    def get(self, request):
        stats = {
            'doctors': Doctor.objects.count(),
            'blood_donors': BloodDonor.objects.count(),
            'ambulances': AmbulanceProfile.objects.count(),
            'diagnostics': DiagnosticProfile.objects.count(),
        }
        return Response(APIResponse.success("Platform stats", "stats", stats))


class AdminDashboardStatsView(APIView):
    """
    Admin Dashboard Stats API providing aggregate platform analytics.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        stats = {
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'inactive': User.objects.filter(is_active=False).count(),
                'doctors': Doctor.objects.count(),
                'doctors_active': Doctor.objects.filter(user__is_active=True).count(),
                'regular': RegularUserProfile.objects.count(),
                'blood_donors': BloodDonor.objects.count(),
                'blood_donors_active': BloodDonor.objects.filter(user__is_active=True).count(),
                'ambulances': AmbulanceProfile.objects.count(),
                'ambulances_active': AmbulanceProfile.objects.filter(user__is_active=True).count(),
                'pharmacies': PharmacyProfile.objects.count(),
                'pharmacies_active': PharmacyProfile.objects.filter(user__is_active=True).count(),
                'diagnostics': DiagnosticProfile.objects.count(),
                'diagnostics_active': DiagnosticProfile.objects.filter(user__is_active=True).count(),
            },
            'posts': {
                'blood_need': BloodNeedPost.objects.count(),
                'medicine_need': MedicineNeedPost.objects.count(),
                'equipment_need': EquipmentNeedPost.objects.count(),
                'general': GeneralPost.objects.count(),
                'total': BloodNeedPost.objects.count() + MedicineNeedPost.objects.count() + EquipmentNeedPost.objects.count() + GeneralPost.objects.count()
            },
            'blogs': {
                'total': BlogPost.objects.count(),
                'published': BlogPost.objects.filter(status='published').count(),
                'draft': BlogPost.objects.filter(status='draft').count(),
            },
            'bookings': {
                'total': DoctorBooking.objects.count(),
                'pending': DoctorBooking.objects.filter(status='pending').count(),
                'confirmed': DoctorBooking.objects.filter(status='confirmed').count(),
                'completed': DoctorBooking.objects.filter(status='completed').count(),
            }
        }
        return Response(APIResponse.success("Admin dashboard statistics retrieved successfully", "stats", stats))


def serve_dashboard(request):
    return render(request, 'dashboard.html')


class AdminLogsView(APIView):
    """
    GET /api/admin/logs/?level=ERROR&search=redis&page=1&limit=50
    Reads the error log file and returns parsed JSON log entries.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        level  = request.query_params.get('level', '').upper()   # ERROR, WARNING, CRITICAL, or '' for all
        search = request.query_params.get('search', '').lower()
        page   = max(1, int(request.query_params.get('page', 1)))
        limit  = min(100, int(request.query_params.get('limit', 50)))

        log_path = os.path.join(settings.BASE_DIR, 'logs', 'medihub_error.log')
        entries = []

        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        # Plain text line — wrap it
                        entry = {'asctime': '', 'levelname': 'INFO', 'name': 'unknown', 'message': line}

                    # Filter by level
                    if level and entry.get('levelname', '').upper() != level:
                        continue
                    # Filter by search
                    if search:
                        haystack = (entry.get('message', '') + entry.get('name', '') + entry.get('exc_info', '')).lower()
                        if search not in haystack:
                            continue

                    # Strip the huge traceback from the list view — keep only first line
                    exc = entry.get('exc_info', '')
                    entry['exc_summary'] = exc.split('\n')[-2].strip() if exc and '\n' in exc else ''
                    entry.pop('exc_info', None)
                    entries.append(entry)
        except FileNotFoundError:
            return Response(APIResponse.success('Log file not found', 'logs', {'entries': [], 'total': 0, 'page': page}))
        except Exception as e:
            return Response({'error': str(e)}, status=500)

        # Newest first
        entries.reverse()
        total  = len(entries)
        start  = (page - 1) * limit
        paged  = entries[start:start + limit]

        # Level counts for the filter badges
        all_entries_for_counts = []
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e2 = json.loads(line)
                        all_entries_for_counts.append(e2.get('levelname', 'INFO').upper())
                    except Exception:
                        pass
        except Exception:
            pass

        level_counts = {}
        for lv in all_entries_for_counts:
            level_counts[lv] = level_counts.get(lv, 0) + 1

        return Response(APIResponse.success('Logs fetched', 'logs', {
            'entries': paged,
            'total': total,
            'page': page,
            'limit': limit,
            'level_counts': level_counts,
        }))

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from medihub.health_check import HealthCheck
from medihub.queue_dashboard import queue_dashboard, TeshMessageQuee
from medihub.views import AdminDashboardStatsView, AdminUserListView, AdminTrafficStatsView, PublicStatsView, AdminLogsView, serve_dashboard
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings as _settings
_swagger_public = _settings.DEBUG
_swagger_perms = [permissions.AllowAny] if _swagger_public else [permissions.IsAdminUser]

schema_view = get_schema_view(
    openapi.Info(
        title='Medihub API',
        default_version='v1',
        description='Medihub platform API documentation',
        contact=openapi.Contact(email='admin@medihub.com'),
    ),
    public=_swagger_public,
    permission_classes=_swagger_perms,
)

def serve_sw(request):
    content = render_to_string('firebase-messaging-sw.js')
    return HttpResponse(content, content_type='application/javascript')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/dashboard-stats/', AdminDashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('api/admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('api/admin/users/<int:user_id>/', AdminUserListView.as_view(), name='admin-user-detail'),
    path('api/admin/traffic/', AdminTrafficStatsView.as_view(), name='admin-traffic'),
    path('api/admin/logs/', AdminLogsView.as_view(), name='admin-logs'),
    path('stats/', PublicStatsView.as_view(), name='public-stats'),
    path('api/stats/', PublicStatsView.as_view(), name='public-stats-api'),
    path('dashboard/', serve_dashboard, name='dashboard'),
    path('firebase-messaging-sw.js', serve_sw),
    path('', HealthCheck),
    path('health/', HealthCheck),
    path('queue/dashboard/', queue_dashboard, name='queue-dashboard'),
    path('queue/test/', TeshMessageQuee, name='queue-test'),
    path('', include('django_prometheus.urls')),
    
    # Core Domain App Routes (no prefix)
    path('doctors/', include('doctor.urls')),
    path('donors/', include('donor.urls')),
    path('ambulances/', include('ambulance.urls')),
    path('pharmacies/', include('pharmacy.urls')),
    path('diagnostics/', include('diagnostic.urls')),

    # API prefixed routes (used by frontend BASE_URL=/api)
    path('api/doctors/', include('doctor.urls')),
    path('api/donors/', include('donor.urls')),
    path('api/ambulances/', include('ambulance.urls')),
    path('api/pharmacies/', include('pharmacy.urls')),
    path('api/diagnostics/', include('diagnostic.urls')),
    path('api/authentication/', include('authentication.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/posts/', include('post.urls')),
    path('api/blogs/', include('blog.urls')),
    path('api/notification/', include('notification.urls')),
    path('api/interactions/', include('interactions.urls')),
    path('api/location/', include('location.urls')),

    # API v1 Versioned Prefix
    path('api/v1/doctors/', include('doctor.urls')),
    path('api/v1/donors/', include('donor.urls')),
    path('api/v1/ambulances/', include('ambulance.urls')),
    path('api/v1/pharmacies/', include('pharmacy.urls')),
    path('api/v1/diagnostics/', include('diagnostic.urls')),

    # Legacy & Platform Routes (no prefix)
    path('authentication/', include('authentication.urls')),
    path('profiles/', include('profiles.urls')),
    path('posts/', include('post.urls')),
    path('blogs/', include('blog.urls')),
    path('notification/', include('notification.urls')),
    path('interactions/', include('interactions.urls')),
    path('location/', include('location.urls')),
    path('', include('feed.urls')),

    # Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
]

# Uploaded profile photos are written under MEDIA_ROOT but nothing was routing
# MEDIA_URL, so every avatar 404'd. In production these are served by nginx.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

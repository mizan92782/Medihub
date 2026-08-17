from django.urls import path, include
from rest_framework.routers import DefaultRouter
from profiles.views import DiagnosticViewSet, DiagnosticTestViewSet

router = DefaultRouter()
router.register(r'tests', DiagnosticTestViewSet, basename='diagnostic-test')
router.register(r'', DiagnosticViewSet, basename='diagnostic')

urlpatterns = [
    path('', include(router.urls)),
]

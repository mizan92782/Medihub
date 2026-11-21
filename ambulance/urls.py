from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AmbulanceViewSet

router = DefaultRouter()
router.register(r'', AmbulanceViewSet, basename='ambulance')

urlpatterns = [
    path('', include(router.urls)),
]

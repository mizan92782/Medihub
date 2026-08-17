from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BloodDonationPostViewSet
from profiles.views import BloodDonorViewSet

router = DefaultRouter()
router.register(r'posts', BloodDonationPostViewSet, basename='donor-post')
router.register(r'', BloodDonorViewSet, basename='donor')

urlpatterns = [
    path('', include(router.urls)),
]

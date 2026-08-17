from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpecializationViewSet
from profiles.views import DoctorViewSet, DoctorBookingViewSet, DoctorRatingViewSet

router = DefaultRouter()
router.register(r'specializations', SpecializationViewSet, basename='doctor-specialization')
router.register(r'bookings', DoctorBookingViewSet, basename='doctor-booking')
router.register(r'ratings', DoctorRatingViewSet, basename='doctor-rating')
router.register(r'', DoctorViewSet, basename='doctor')

urlpatterns = [
    path('', include(router.urls)),
]

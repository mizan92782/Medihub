from rest_framework.routers import DefaultRouter
from profiles.views import (
    UserProfileViewSet,
    DoctorViewSet,
    DoctorRatingViewSet,
    DoctorBookingViewSet,
    BloodDonorViewSet,
    AmbulanceViewSet,
    PharmacyViewSet,
    PharmacyMedicineViewSet,
    DiagnosticViewSet,
    DiagnosticTestViewSet,
    MedicalMetadataViewSet,
)

router = DefaultRouter()
router.register('users', UserProfileViewSet, basename='user-profile')
router.register('doctors', DoctorViewSet, basename='doctor')
router.register('ratings', DoctorRatingViewSet, basename='doctor-rating')
router.register('bookings', DoctorBookingViewSet, basename='doctor-booking')
router.register('blood-donors', BloodDonorViewSet, basename='blood-donor')
router.register('ambulances', AmbulanceViewSet, basename='ambulance')
router.register('pharmacies', PharmacyViewSet, basename='pharmacy')
router.register('medicines', PharmacyMedicineViewSet, basename='pharmacy-medicine')
router.register('diagnostics', DiagnosticViewSet, basename='diagnostic')
router.register('diagnostic-tests', DiagnosticTestViewSet, basename='diagnostic-test')
router.register('metadata', MedicalMetadataViewSet, basename='medical-metadata')

urlpatterns = router.urls

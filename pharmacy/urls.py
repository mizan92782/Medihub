from django.urls import path, include
from rest_framework.routers import DefaultRouter
from profiles.views import PharmacyViewSet, PharmacyMedicineViewSet

router = DefaultRouter()
router.register(r'medicines', PharmacyMedicineViewSet, basename='pharmacy-medicine')
router.register(r'', PharmacyViewSet, basename='pharmacy')

urlpatterns = [
    path('', include(router.urls)),
]

from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsPharmacyUser, IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import PharmacyProfile, PharmacyMedicine
from .serializers import PharmacyProfileSerializer, PharmacyMedicineSerializer

class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = PharmacyProfile.objects.all()
    serializer_class = PharmacyProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_open', 'division', 'district']
    search_fields = ['pharmacy_name', 'license_number', 'contact_number']

class PharmacyMedicineViewSet(viewsets.ModelViewSet):
    queryset = PharmacyMedicine.objects.all().select_related('pharmacy')
    serializer_class = PharmacyMedicineSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['pharmacy', 'in_stock']
    search_fields = ['name', 'generic_name', 'brand_name']

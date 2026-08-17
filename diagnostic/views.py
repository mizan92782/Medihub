from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsDiagnosticUser, IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import DiagnosticProfile, DiagnosticTest
from .serializers import DiagnosticProfileSerializer, DiagnosticTestSerializer

class DiagnosticViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticProfile.objects.all()
    serializer_class = DiagnosticProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_open', 'division', 'district']
    search_fields = ['diagnostic_name', 'license_number', 'contact_number']

class DiagnosticTestViewSet(viewsets.ModelViewSet):
    queryset = DiagnosticTest.objects.all().select_related('diagnostic')
    serializer_class = DiagnosticTestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['diagnostic', 'category', 'is_available']
    search_fields = ['test_name', 'category', 'preparation_instructions']

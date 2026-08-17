from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsAmbulanceUser, IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import AmbulanceProfile
from .serializers import AmbulanceProfileSerializer

class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = AmbulanceProfile.objects.all()
    serializer_class = AmbulanceProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ambulance_type']
    search_fields = ['owner_name', 'vehicle_number', 'contact_number', 'address']

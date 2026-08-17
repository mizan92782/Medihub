from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsBloodDonorUser, IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import BloodDonor, BloodDonationPost
from .serializers import BloodDonorSerializer, BloodDonationPostSerializer

class BloodDonorViewSet(viewsets.ModelViewSet):
    queryset = BloodDonor.objects.all().select_related('division', 'district', 'upozila')
    serializer_class = BloodDonorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['blood_group', 'availability', 'division', 'district']
    search_fields = ['first_name', 'last_name', 'blood_group', 'district_name']

class BloodDonationPostViewSet(viewsets.ModelViewSet):
    queryset = BloodDonationPost.objects.all().select_related('donor')
    serializer_class = BloodDonationPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

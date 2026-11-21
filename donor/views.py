from rest_framework import viewsets, filters, permissions
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsBloodDonorUser, IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import BloodDonor, BloodDonationPost
from .serializers import BloodDonorSerializer, BloodDonationPostSerializer

class BloodDonorViewSet(viewsets.ModelViewSet):
    serializer_class = BloodDonorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blood_group', 'availability', 'division', 'district', 'upozila']

    def get_queryset(self):
        qs = BloodDonor.objects.all().select_related('division', 'district', 'upozila').filter(is_active=True, user__is_blocked=False)
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(blood_group__icontains=search) |
                Q(address__icontains=search) |
                Q(division__division_name_eng__icontains=search) |
                Q(division__division_name_bn__icontains=search) |
                Q(district__district_name_eng__icontains=search) |
                Q(district__district_name_bn__icontains=search) |
                Q(upozila__upozila_name_eng__icontains=search) |
                Q(upozila__upoila_name_bn__icontains=search)
            )
        return qs

class BloodDonationPostViewSet(viewsets.ModelViewSet):
    queryset = BloodDonationPost.objects.all().select_related('donor')
    serializer_class = BloodDonationPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

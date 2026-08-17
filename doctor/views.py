from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsDoctorUser, IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import Doctor, Specialization, DoctorBooking, DoctorRating
from .serializers import (
    DoctorSerializer, SpecializationSerializer,
    DoctorBookingSerializer, DoctorRatingSerializer
)

class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all().select_related('specialization', 'division', 'district', 'evaluation').prefetch_related('qualifications', 'hospital_affiliations')
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'division', 'district', 'gender']
    search_fields = ['first_name', 'last_name', 'specialization__name_eng', 'license_number']
    ordering_fields = ['created', 'years_of_experience']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"success": True, "message": "Doctor profile created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    pagination_class = StandardResultsSetPagination

class DoctorBookingViewSet(viewsets.ModelViewSet):
    queryset = DoctorBooking.objects.all().select_related('doctor', 'patient')
    serializer_class = DoctorBookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

class DoctorRatingViewSet(viewsets.ModelViewSet):
    queryset = DoctorRating.objects.all()
    serializer_class = DoctorRatingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

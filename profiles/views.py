from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination
from core.permissions import (
    IsOwnerOrReadOnly,
    IsDoctorUser,
    IsRegularUser,
    IsBloodDonorUser,
    IsAmbulanceUser,
    IsPharmacyUser,
    IsDiagnosticUser,
)
from profiles.models import (
    RegularUserProfile,
    Doctor,
    DoctorDetails,
    DoctorEducation,
    DoctorWorkingExperience,
    DoctorScheduling,
    DoctorDateSlot,
    DoctorRating,
    DoctorBooking,
    DoctorStats,
    Specialization,
    SubSpecialization,
    Qualification,
    Hospital,
    BloodDonor,
    BloodDonationPost,
    AmbulanceProfile,
    PharmacyProfile,
    PharmacyMedicine,
    DiagnosticProfile,
    DiagnosticTest,
)
from profiles.serializers import (
    RegularUserProfileSerializer,
    DoctorProfileSerializer,
    DoctorDetailsSerializer,
    DoctorEducationSerializer,
    DoctorWorkingExperienceSerializer,
    DoctorSchedulingSerializer,
    DoctorDateSlotSerializer,
    DoctorRatingSerializer,
    DoctorBookingSerializer,
    BloodDonorProfileSerializer,
    BloodDonationPostSerializer,
    AmbulanceProfileSerializer,
    PharmacyProfileSerializer,
    PharmacyMedicineSerializer,
    DiagnosticProfileSerializer,
    DiagnosticTestSerializer,
    SpecializationSerializer,
    SubSpecializationSerializer,
    QualificationSerializer,
    HospitalSerializer,
)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for current logged in Regular User Profile.
    """
    serializer_class = RegularUserProfileSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return RegularUserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        profile, created = RegularUserProfile.objects.get_or_create(
            user=request.user,
            defaults={'first_name': request.user.email.split('@')[0], 'last_name': 'User'}
        )
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(APIResponse.success("User profile retrieved successfully", "profile", serializer.data))
        else:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(APIResponse.success("User profile updated successfully", "profile", serializer.data))


class DoctorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Doctor Search, Filter, and Management.
    """
    serializer_class = DoctorProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'sub_specialization', 'division', 'district', 'upozila', 'gender']
    search_fields = ['first_name', 'last_name', 'specialization__name_eng', 'qualifications__name_eng']
    ordering_fields = ['years_of_experience', 'evaluation__avg_rating', 'created']

    def get_queryset(self):
        return Doctor.objects.select_related(
            'user', 'specialization', 'sub_specialization', 'division', 'district', 'upozila', 'union', 'details', 'evaluation'
        ).prefetch_related('qualifications', 'hospital_affiliations', 'educations', 'experiences', 'schedules').all()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsDoctorUser], url_path='me')
    def me(self, request):
        doctor = Doctor.objects.filter(user=request.user).first()
        if not doctor:
            return Response(APIResponse.error("Doctor profile not found"), status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = self.get_serializer(doctor)
            return Response(APIResponse.success("Doctor profile retrieved successfully", "doctor", serializer.data))
        else:
            serializer = self.get_serializer(doctor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(APIResponse.success("Doctor profile updated successfully", "doctor", serializer.data))

    @action(detail=True, methods=['post'], permission_classes=[IsDoctorUser], url_path='details')
    def add_update_details(self, request, pk=None):
        doctor = self.get_object()
        details, _ = DoctorDetails.objects.get_or_create(doctor=doctor)
        serializer = DoctorDetailsSerializer(details, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(APIResponse.success("Doctor details updated", "details", serializer.data))

    @action(detail=True, methods=['post'], permission_classes=[IsDoctorUser], url_path='education')
    def add_education(self, request, pk=None):
        doctor = self.get_object()
        serializer = DoctorEducationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(doctor=doctor)
        return Response(APIResponse.success("Education added", "education", serializer.data), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsDoctorUser], url_path='experience')
    def add_experience(self, request, pk=None):
        doctor = self.get_object()
        serializer = DoctorWorkingExperienceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(doctor=doctor)
        return Response(APIResponse.success("Experience added", "experience", serializer.data), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsDoctorUser], url_path='schedule')
    def add_schedule(self, request, pk=None):
        doctor = self.get_object()
        serializer = DoctorSchedulingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(doctor=doctor)
        return Response(APIResponse.success("Schedule added", "schedule", serializer.data), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsDoctorUser], url_path='my-slots')
    def list_my_date_slots(self, request):
        doctor = Doctor.objects.filter(user=request.user).first()
        if not doctor:
            return Response(APIResponse.error("Doctor profile not found"), status=status.HTTP_404_NOT_FOUND)
        
        # Auto-generate slots for the next 14 days based on weekly schedules
        import datetime
        from django.utils import timezone
        schedules = doctor.schedules.all()
        today = timezone.localtime(timezone.now()).date()

        for i in range(15):
            target_date = today + datetime.timedelta(days=i)
            target_weekday_name = target_date.strftime('%A').lower()
            for sched in schedules:
                if sched.day == target_weekday_name:
                    # check if DateSlot already exists
                    DoctorDateSlot.objects.get_or_create(
                        schedule=sched,
                        date=target_date,
                        defaults={
                            'max_patients': sched.max_patients,
                            'is_approved': False
                        }
                    )
                    
        # Return all doctor slots ordered by date
        from django.db.models import F
        date_slots = DoctorDateSlot.objects.filter(schedule__doctor=doctor, date__gte=today).order_by('date', 'schedule__start')
        serializer = DoctorDateSlotSerializer(date_slots, many=True)
        return Response(APIResponse.success("Upcoming slots retrieved", "slots", serializer.data))

    @action(detail=False, methods=['post'], permission_classes=[IsDoctorUser], url_path='toggle-slot')
    def toggle_slot_approval(self, request):
        slot_id = request.data.get('slot_id')
        if not slot_id:
            return Response(APIResponse.error("slot_id is required"), status=status.HTTP_400_BAD_REQUEST)
        slot = DoctorDateSlot.objects.filter(id=slot_id, schedule__doctor__user=request.user).first()
        if not slot:
            return Response(APIResponse.error("Slot not found"), status=status.HTTP_404_NOT_FOUND)
        
        slot.is_approved = not slot.is_approved
        slot.save()
        
        return Response(APIResponse.success("Slot approval status toggled", "slot", DoctorDateSlotSerializer(slot).data))

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='available-slots')
    def available_slots(self, request, pk=None):
        doctor = self.get_object()
        from django.utils import timezone
        from django.db.models import F
        today = timezone.localtime(timezone.now()).date()
        slots = DoctorDateSlot.objects.filter(
            schedule__doctor=doctor,
            date__gte=today,
            is_approved=True,
            bookings_count__lt=F('max_patients')
        ).order_by('date', 'schedule__start')
        serializer = DoctorDateSlotSerializer(slots, many=True)
        return Response(APIResponse.success("Available slots retrieved", "slots", serializer.data))


class DoctorRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for rating doctors. Unique per user per doctor.
    """
    serializer_class = DoctorRatingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return DoctorRating.objects.all()

    def create(self, request, *args, **kwargs):
        doctor_id = request.data.get('doctor')
        rating_val = request.data.get('rating')
        review = request.data.get('review', '')
        if not doctor_id or not rating_val:
            return Response(APIResponse.error("doctor and rating are required fields"), status=status.HTTP_400_BAD_REQUEST)
        
        doctor = Doctor.objects.filter(pk=doctor_id).first()
        if not doctor:
            return Response(APIResponse.error("Doctor not found"), status=status.HTTP_404_NOT_FOUND)

        rating_obj, created = DoctorRating.objects.update_or_create(
            doctor=doctor,
            user=request.user,
            defaults={'rating': rating_val, 'review': review}
        )
        serializer = self.get_serializer(rating_obj)
        return Response(
            APIResponse.success("Doctor rated successfully", "rating", serializer.data),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class DoctorBookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for booking doctor appointments.
    """
    serializer_class = DoctorBookingSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'doctor', 'appointment_date']

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'doctor' and hasattr(user, 'doctor'):
            return DoctorBooking.objects.filter(doctor=user.doctor)
        return DoctorBooking.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ValueError as e:
            return Response(APIResponse.error(str(e)), status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        return Response(APIResponse.success("Booking created successfully", "booking", serializer.data), status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BloodDonorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Blood Donor profile, search/filtering, availability, and donation posts.
    """
    serializer_class = BloodDonorProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['blood_group', 'availability', 'division', 'district', 'upozila', 'gender']
    search_fields = ['first_name', 'last_name', 'address']

    def get_queryset(self):
        return BloodDonor.objects.select_related('user', 'division', 'district', 'upozila').prefetch_related('donation_posts').all()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsBloodDonorUser], url_path='me')
    def me(self, request):
        donor = BloodDonor.objects.filter(user=request.user).first()
        if not donor:
            return Response(APIResponse.error("Blood donor profile not found"), status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = self.get_serializer(donor)
            return Response(APIResponse.success("Donor profile retrieved", "donor", serializer.data))
        else:
            serializer = self.get_serializer(donor, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(APIResponse.success("Donor profile updated", "donor", serializer.data))

    @action(detail=False, methods=['post'], permission_classes=[IsBloodDonorUser], url_path='donation-post')
    def create_donation_post(self, request):
        donor = BloodDonor.objects.filter(user=request.user).first()
        if not donor:
            return Response(APIResponse.error("Only registered blood donors can create donation posts"), status=status.HTTP_403_FORBIDDEN)
        serializer = BloodDonationPostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(donor=donor)
        return Response(APIResponse.success("Donation post created successfully and life counter incremented!", "donation_post", serializer.data), status=status.HTTP_201_CREATED)


class AmbulanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ambulance Service Provider profile and search.
    """
    serializer_class = AmbulanceProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ambulance_type', 'is_available', 'division', 'district', 'upozila']
    search_fields = ['owner_name', 'vehicle_number', 'address']

    def get_queryset(self):
        return AmbulanceProfile.objects.select_related('user', 'division', 'district', 'upozila').all()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAmbulanceUser], url_path='me')
    def me(self, request):
        ambulance = AmbulanceProfile.objects.filter(user=request.user).first()
        if not ambulance:
            return Response(APIResponse.error("Ambulance profile not found"), status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = self.get_serializer(ambulance)
            return Response(APIResponse.success("Ambulance profile retrieved", "ambulance", serializer.data))
        else:
            serializer = self.get_serializer(ambulance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(APIResponse.success("Ambulance profile updated", "ambulance", serializer.data))


class PharmacyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Pharmacy search, profile, and Medicine inventory.
    """
    serializer_class = PharmacyProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_open', 'division', 'district', 'upozila']
    search_fields = ['pharmacy_name', 'owner_name', 'license_number', 'address']

    def get_queryset(self):
        return PharmacyProfile.objects.select_related('user', 'division', 'district', 'upozila').all()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsPharmacyUser], url_path='me')
    def me(self, request):
        pharmacy = PharmacyProfile.objects.filter(user=request.user).first()
        if not pharmacy:
            return Response(APIResponse.error("Pharmacy profile not found"), status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = self.get_serializer(pharmacy)
            return Response(APIResponse.success("Pharmacy profile retrieved", "pharmacy", serializer.data))
        else:
            serializer = self.get_serializer(pharmacy, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(APIResponse.success("Pharmacy profile updated", "pharmacy", serializer.data))


class PharmacyMedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Pharmacy Medicine Inventory & Public Search.
    """
    serializer_class = PharmacyMedicineSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pharmacy', 'category', 'in_stock']
    search_fields = ['name', 'generic_name', 'brand_name', 'category', 'description']
    ordering_fields = ['price', 'name', 'created']

    def get_queryset(self):
        return PharmacyMedicine.objects.select_related('pharmacy').all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'pharmacy':
            return Response(APIResponse.error("Only registered pharmacies can add medicines"), status=status.HTTP_403_FORBIDDEN)
        pharmacy = PharmacyProfile.objects.filter(user=request.user).first()
        if not pharmacy:
            return Response(APIResponse.error("Pharmacy profile missing"), status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(pharmacy=pharmacy)
        return Response(APIResponse.success("Medicine added successfully", "medicine", serializer.data), status=status.HTTP_201_CREATED)


class DiagnosticViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Diagnostic Center search, profile, and Test catalog.
    """
    serializer_class = DiagnosticProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_open', 'division', 'district', 'upozila']
    search_fields = ['diagnostic_name', 'owner_name', 'license_number', 'address']

    def get_queryset(self):
        return DiagnosticProfile.objects.select_related('user', 'division', 'district', 'upozila').all()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsDiagnosticUser], url_path='me')
    def me(self, request):
        diagnostic = DiagnosticProfile.objects.filter(user=request.user).first()
        if not diagnostic:
            return Response(APIResponse.error("Diagnostic profile not found"), status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            serializer = self.get_serializer(diagnostic)
            return Response(APIResponse.success("Diagnostic profile retrieved", "diagnostic", serializer.data))
        else:
            serializer = self.get_serializer(diagnostic, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(APIResponse.success("Diagnostic profile updated", "diagnostic", serializer.data))


class DiagnosticTestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Diagnostic Test Catalog & Public Search.
    """
    serializer_class = DiagnosticTestSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['diagnostic', 'category', 'is_available']
    search_fields = ['test_name', 'category', 'description', 'preparation_instructions']
    ordering_fields = ['price', 'test_name', 'created']

    def get_queryset(self):
        return DiagnosticTest.objects.select_related('diagnostic').all()

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'diagnostic':
            return Response(APIResponse.error("Only registered diagnostic centers can add tests"), status=status.HTTP_403_FORBIDDEN)
        diagnostic = DiagnosticProfile.objects.filter(user=request.user).first()
        if not diagnostic:
            return Response(APIResponse.error("Diagnostic profile missing"), status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(diagnostic=diagnostic)
        return Response(APIResponse.success("Diagnostic test added successfully", "test", serializer.data), status=status.HTTP_201_CREATED)


class MedicalMetadataViewSet(viewsets.ViewSet):
    """
    ReadOnly metadata endpoints for Specializations, SubSpecializations, Qualifications, Hospitals.
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='specializations')
    def list_specializations(self, request):
        qs = Specialization.objects.prefetch_related('sub_specializations').all()
        serializer = SpecializationSerializer(qs, many=True)
        return Response(APIResponse.success("Specializations retrieved", "specializations", serializer.data))

    @action(detail=False, methods=['get'], url_path='sub-specializations')
    def list_sub_specializations(self, request):
        spec_id = request.query_params.get('specialization')
        qs = SubSpecialization.objects.all()
        if spec_id:
            qs = qs.filter(specialization_id=spec_id)
        serializer = SubSpecializationSerializer(qs, many=True)
        return Response(APIResponse.success("SubSpecializations retrieved", "sub_specializations", serializer.data))

    @action(detail=False, methods=['get'], url_path='qualifications')
    def list_qualifications(self, request):
        qs = Qualification.objects.all()
        serializer = QualificationSerializer(qs, many=True)
        return Response(APIResponse.success("Qualifications retrieved", "qualifications", serializer.data))

    @action(detail=False, methods=['get'], url_path='hospitals')
    def list_hospitals(self, request):
        qs = Hospital.objects.all()
        serializer = HospitalSerializer(qs, many=True)
        return Response(APIResponse.success("Hospitals retrieved", "hospitals", serializer.data))

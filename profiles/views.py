from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from cache.keys import CacheKeys
from cache.manager import CacheManager
from cache.ttl import CacheTTL
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
    IsAdminUser,
)
from profiles.models import (
    PracticeLocation,
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
    PracticeLocationSerializer,
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
    ViewSet for current logged in Regular User Profile and public profile view.
    """
    serializer_class = RegularUserProfileSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.action in ['retrieve', 'list', 'by_user']:
            return RegularUserProfile.objects.filter(is_active=True, user__is_blocked=False)
        return RegularUserProfile.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(APIResponse.success("User profile retrieved", "profile", serializer.data))

    @action(detail=False, methods=['get'], url_path='by-user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        profile = RegularUserProfile.objects.filter(user_id=user_id, is_active=True, user__is_blocked=False).first()
        if not profile:
            from authentication.models import User
            user = User.objects.filter(id=user_id, is_blocked=False).first()
            if user:
                profile, _ = RegularUserProfile.objects.get_or_create(
                    user=user,
                    defaults={'first_name': user.email.split('@')[0], 'last_name': 'Member'}
                )
            else:
                return Response(APIResponse.error("Profile not found"), status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(profile)
        return Response(APIResponse.success("User profile retrieved", "profile", serializer.data))

    def list(self, request, *args, **kwargs):
        # Public listing only shows active, non-blocked profiles
        qs = RegularUserProfile.objects.filter(is_active=True, user__is_blocked=False)
        serializer = self.get_serializer(qs, many=True)
        return Response(APIResponse.success("Profiles retrieved", "profiles", serializer.data))

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated], url_path='me')
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

    @action(detail=False, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request):
        """User can activate/deactivate their own profile visibility."""
        profile, _ = RegularUserProfile.objects.get_or_create(
            user=request.user,
            defaults={'first_name': request.user.email.split('@')[0], 'last_name': 'User'}
        )
        profile.is_active = not profile.is_active
        profile.save(update_fields=['is_active'])
        state = 'active' if profile.is_active else 'inactive'
        return Response(APIResponse.success(f"Profile is now {state}.", "is_active", profile.is_active))

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='block')
    def block_user(self, request, pk=None):
        """Admin can block a user account. Blocked users cannot login."""
        profile = self.get_object()
        profile.user.is_blocked = True
        profile.user.save(update_fields=['is_blocked'])
        return Response(APIResponse.success("User has been blocked.", "is_blocked", True))

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], url_path='unblock')
    def unblock_user(self, request, pk=None):
        """Admin can unblock a user account."""
        profile = self.get_object()
        profile.user.is_blocked = False
        profile.user.save(update_fields=['is_blocked'])
        return Response(APIResponse.success("User has been unblocked.", "is_blocked", False))


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
        ).prefetch_related('qualifications', 'hospital_affiliations', 'affiliations', 'educations', 'experiences', 'schedules').filter(is_active=True, user__is_blocked=False)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        cache_key = CacheKeys.DoctorProfile(pk)
        cached = CacheManager.GetCache(cache_key)
        if cached['success']:
            return Response(APIResponse.success("Doctor profile retrieved", "doctor", cached['data']))
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        CacheManager.SetCache(cache_key, serializer.data, CacheTTL.LARGE)
        return Response(APIResponse.success("Doctor profile retrieved", "doctor", serializer.data))

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
            CacheManager.DeleteCache(CacheKeys.DoctorTab(doctor.id, 'expertise'))
            CacheManager.DeleteCache(CacheKeys.DoctorProfile(doctor.id))
            return Response(APIResponse.success("Doctor profile updated successfully", "doctor", serializer.data))

    @action(detail=False, methods=['post'], permission_classes=[IsDoctorUser], url_path='toggle-active')
    def toggle_active(self, request):
        """Doctor can activate/deactivate their own profile visibility."""
        doctor = Doctor.objects.filter(user=request.user).first()
        if not doctor:
            return Response(APIResponse.error("Doctor profile not found"), status=status.HTTP_404_NOT_FOUND)
        doctor.is_active = not doctor.is_active
        doctor.save(update_fields=['is_active'])
        state = 'active' if doctor.is_active else 'inactive'
        return Response(APIResponse.success(f"Profile is now {state}.", "is_active", doctor.is_active))

    @action(detail=False, methods=['post'], permission_classes=[IsDoctorUser], url_path='expertise-areas')
    def update_expertise_areas(self, request):
        doctor = Doctor.objects.filter(user=request.user).first()
        if not doctor:
            return Response(APIResponse.error("Doctor profile not found"), status=status.HTTP_404_NOT_FOUND)
        areas = request.data.get('expertise_areas', [])
        if not isinstance(areas, list):
            return Response(APIResponse.error("expertise_areas must be a list"), status=status.HTTP_400_BAD_REQUEST)
        doctor.expertise_areas = areas
        doctor.save(update_fields=['expertise_areas'])
        CacheManager.DeleteCache(CacheKeys.DoctorTab(doctor.id, 'expertise'))
        return Response(APIResponse.success("Expertise areas updated", "expertise_areas", doctor.expertise_areas))

    @action(detail=True, methods=['post'], permission_classes=[IsDoctorUser], url_path='details')
    def add_update_details(self, request, pk=None):
        doctor = self.get_object()
        details, _ = DoctorDetails.objects.get_or_create(doctor=doctor)
        serializer = DoctorDetailsSerializer(details, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(APIResponse.success("Doctor details updated", "details", serializer.data))

    @action(detail=True, methods=['post', 'put', 'patch', 'delete'], permission_classes=[IsDoctorUser], url_path='education')
    def manage_education(self, request, pk=None):
        doctor = self.get_object()
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            inst_name = request.data.get('institution')
            if inst_name:
                stripped = inst_name.strip()
                if stripped:
                    from profiles.models.doctor_prof_mod import Hospital
                    exists = Hospital.objects.filter(name_eng__iexact=stripped).exists() or Hospital.objects.filter(name_bn__iexact=stripped).exists()
                    if not exists:
                        Hospital.objects.create(name_eng=stripped, name_bn=stripped)

        if request.method == 'POST':
            serializer = DoctorEducationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(doctor=doctor)
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'education'))
            return Response(APIResponse.success("Education added", "education", serializer.data), status=status.HTTP_201_CREATED)
        elif request.method in ['PUT', 'PATCH']:
            edu_id = request.query_params.get('id') or request.data.get('id')
            if not edu_id:
                return Response(APIResponse.error("Education ID is required"), status=status.HTTP_400_BAD_REQUEST)
            edu = DoctorEducation.objects.filter(doctor=doctor, id=edu_id).first()
            if not edu:
                return Response(APIResponse.error("Education not found"), status=status.HTTP_404_NOT_FOUND)
            serializer = DoctorEducationSerializer(edu, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'education'))
            return Response(APIResponse.success("Education updated successfully", "education", serializer.data))
        elif request.method == 'DELETE':
            edu_id = request.query_params.get('id')
            if not edu_id:
                return Response(APIResponse.error("Education ID is required"), status=status.HTTP_400_BAD_REQUEST)
            edu = DoctorEducation.objects.filter(doctor=doctor, id=edu_id).first()
            if not edu:
                return Response(APIResponse.error("Education not found"), status=status.HTTP_404_NOT_FOUND)
            edu.delete()
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'education'))
            return Response(APIResponse.success("Education deleted successfully"), status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsDoctorUser], url_path='experience')
    def manage_experience(self, request, pk=None):
        doctor = self.get_object()
        if request.method == 'POST':
            serializer = DoctorWorkingExperienceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(doctor=doctor)
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'experience'))
            return Response(APIResponse.success("Experience added", "experience", serializer.data), status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            exp_id = request.query_params.get('id')
            if not exp_id:
                return Response(APIResponse.error("Experience ID is required"), status=status.HTTP_400_BAD_REQUEST)
            exp = DoctorWorkingExperience.objects.filter(doctor=doctor, id=exp_id).first()
            if not exp:
                return Response(APIResponse.error("Experience not found"), status=status.HTTP_404_NOT_FOUND)
            exp.delete()
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'experience'))
            return Response(APIResponse.success("Experience deleted successfully"), status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'put', 'patch', 'delete'], permission_classes=[IsDoctorUser], url_path='affiliation')
    def manage_affiliation(self, request, pk=None):
        doctor = self.get_object()
        from profiles.models.doctor_prof_mod import DoctorAffiliation
        from profiles.serializers import DoctorAffiliationSerializer

        if request.method == 'POST':
            serializer = DoctorAffiliationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(doctor=doctor)
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'about'))
            CacheManager.DeleteCache(CacheKeys.DoctorProfile(pk))
            return Response(APIResponse.success("Affiliation added successfully", "affiliation", serializer.data), status=status.HTTP_201_CREATED)
        elif request.method in ['PUT', 'PATCH']:
            aff_id = request.query_params.get('id') or request.data.get('id')
            if not aff_id:
                return Response(APIResponse.error("Affiliation ID is required"), status=status.HTTP_400_BAD_REQUEST)
            aff = DoctorAffiliation.objects.filter(doctor=doctor, id=aff_id).first()
            if not aff:
                return Response(APIResponse.error("Affiliation not found"), status=status.HTTP_404_NOT_FOUND)
            serializer = DoctorAffiliationSerializer(aff, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'about'))
            CacheManager.DeleteCache(CacheKeys.DoctorProfile(pk))
            return Response(APIResponse.success("Affiliation updated successfully", "affiliation", serializer.data))
        elif request.method == 'DELETE':
            aff_id = request.query_params.get('id')
            if not aff_id:
                return Response(APIResponse.error("Affiliation ID is required"), status=status.HTTP_400_BAD_REQUEST)
            aff = DoctorAffiliation.objects.filter(doctor=doctor, id=aff_id).first()
            if not aff:
                return Response(APIResponse.error("Affiliation not found"), status=status.HTTP_404_NOT_FOUND)
            aff.delete()
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'about'))
            CacheManager.DeleteCache(CacheKeys.DoctorProfile(pk))
            return Response(APIResponse.success("Affiliation deleted successfully"), status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsDoctorUser], url_path='schedule')
    def manage_schedule(self, request, pk=None):
        doctor = self.get_object()
        if request.method == 'POST':
            serializer = DoctorSchedulingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(doctor=doctor)
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'schedule'))
            return Response(APIResponse.success("Schedule added", "schedule", serializer.data), status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            sch_id = request.query_params.get('id')
            if not sch_id:
                return Response(APIResponse.error("Schedule ID is required"), status=status.HTTP_400_BAD_REQUEST)
            sch = DoctorScheduling.objects.filter(doctor=doctor, id=sch_id).first()
            if not sch:
                return Response(APIResponse.error("Schedule not found"), status=status.HTTP_404_NOT_FOUND)
            sch.delete()
            CacheManager.DeleteCache(CacheKeys.DoctorTab(pk, 'schedule'))
            return Response(APIResponse.success("Schedule deleted successfully"), status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsDoctorUser], url_path='my-slots')
    def list_my_date_slots(self, request):
        doctor = Doctor.objects.filter(user=request.user).first()
        if not doctor:
            return Response(APIResponse.error("Doctor profile not found"), status=status.HTTP_404_NOT_FOUND)
        
        import datetime
        from django.utils import timezone
        schedules = doctor.schedules.filter(is_active=True)
        today = timezone.localtime(timezone.now()).date()

        for sched in schedules:
            # Determine generation window from valid_from / valid_until
            start = max(sched.valid_from, today) if sched.valid_from else today
            end = sched.valid_until if sched.valid_until else None
            if end is None:
                # No end date set — do not auto-generate
                continue
            if end < today:
                continue
            current = start
            while current <= end:
                if current.strftime('%A').lower() == sched.day:
                    DoctorDateSlot.objects.get_or_create(
                        schedule=sched,
                        date=current,
                        defaults={'max_patients': sched.max_patients, 'is_approved': True}
                    )
                current += datetime.timedelta(days=1)
                    
        # Return all doctor slots ordered by date
        date_slots = DoctorDateSlot.objects.filter(
            schedule__doctor=doctor, date__gte=today
        ).select_related(
            'schedule', 'schedule__practice_location', 'schedule__hospital'
        ).prefetch_related('bookings').order_by('date', 'schedule__start')
        serializer = DoctorDateSlotSerializer(date_slots, many=True)
        return Response(APIResponse.success("Upcoming slots retrieved", "slots", serializer.data))

    @action(detail=False, methods=['post'], permission_classes=[IsDoctorUser], url_path='toggle-slot-status')
    def toggle_slot_status(self, request):
        slot_id = request.data.get('slot_id')
        new_status = request.data.get('status')
        confirm_override = request.data.get('confirm') == True
        
        if not slot_id or not new_status:
            return Response(APIResponse.error("slot_id and status are required"), status=status.HTTP_400_BAD_REQUEST)
            
        slot = DoctorDateSlot.objects.filter(id=slot_id, schedule__doctor__user=request.user).first()
        if not slot:
            return Response(APIResponse.error("Slot not found"), status=status.HTTP_404_NOT_FOUND)

        if new_status in ['paused', 'cancelled'] and slot.status == 'open':
            active_bookings = slot.bookings.filter(status__in=['pending', 'confirmed'])
            if active_bookings.exists() and not confirm_override:
                return Response({
                    "status": False,
                    "code": "HAS_ACTIVE_APPOINTMENTS",
                    "message": f"This session has {active_bookings.count()} active patient appointments. Are you sure you want to pause/cancel it?",
                    "count": active_bookings.count()
                }, status=status.HTTP_200_OK)
                
            if active_bookings.exists() and confirm_override:
                for b in active_bookings:
                    b.status = 'cancelled_by_doctor';
                    b.save()
        
        slot.status = new_status
        slot.is_approved = (new_status == 'open')
        slot.save()
        
        return Response(APIResponse.success("Slot status updated successfully", "slot", DoctorDateSlotSerializer(slot).data))

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

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='tab/(?P<tab_name>[^/.]+)')
    def tab_data(self, request, pk=None, tab_name=None):
        """
        Returns only the data needed for a specific profile tab.
        Cached in Redis per doctor+tab to reduce DB load.
        Supported tabs: about, education, experience, schedule, stats
        """
        VALID_TABS = {'about', 'education', 'experience', 'expertise', 'practice_locations', 'affiliations', 'schedule', 'stats'}
        if tab_name not in VALID_TABS:
            return Response(APIResponse.error(f"Invalid tab. Choose from: {', '.join(VALID_TABS)}"), status=status.HTTP_400_BAD_REQUEST)

        cache_key = CacheKeys.DoctorTab(pk, tab_name)
        cached = CacheManager.GetCache(cache_key)
        if cached['success']:
            return Response(APIResponse.success(f"{tab_name} tab data retrieved", "data", cached['data']))

        doctor = self.get_object()

        if tab_name == 'about':
            from profiles.serializers import HospitalSerializer, DoctorAffiliationSerializer
            data = {
                'bio': doctor.details.bio if hasattr(doctor, 'details') and doctor.details else None,
                'language': doctor.details.language if hasattr(doctor, 'details') and doctor.details else None,
                'website': doctor.details.website if hasattr(doctor, 'details') and doctor.details else None,
                'license_number': doctor.license_number,
                'hospitals_detail': HospitalSerializer(doctor.hospital_affiliations.all(), many=True).data,
                'affiliations_detail': DoctorAffiliationSerializer(doctor.affiliations.all(), many=True).data,
            }
        elif tab_name == 'education':
            from profiles.serializers import DoctorEducationSerializer
            data = {'educations': DoctorEducationSerializer(doctor.educations.all().order_by('start_at'), many=True).data}
        elif tab_name == 'experience':
            from profiles.serializers import DoctorWorkingExperienceSerializer
            data = {'experiences': DoctorWorkingExperienceSerializer(doctor.experiences.all().order_by('starting_at'), many=True).data}
        elif tab_name == 'expertise':
            from profiles.serializers import SpecializationSerializer, SubSpecializationSerializer, QualificationSerializer
            data = {
                'specialization': SpecializationSerializer(doctor.specialization).data if doctor.specialization else None,
                'sub_specialization': SubSpecializationSerializer(doctor.sub_specialization).data if doctor.sub_specialization else None,
                'qualifications': QualificationSerializer(doctor.qualifications.all(), many=True).data,
                'years_of_experience': doctor.years_of_experience,
                'expertise_areas': doctor.expertise_areas or [],
            }
        elif tab_name == 'practice_locations':
            import datetime
            from django.utils import timezone

            today = timezone.localtime(timezone.now()).date()

            # Auto-generate slots only within doctor-defined valid_from/valid_until range
            schedules = doctor.schedules.filter(is_active=True)
            for sched in schedules:
                start = max(sched.valid_from, today) if sched.valid_from else today
                end = sched.valid_until
                if not end or end < today:
                    continue
                current = start
                while current <= end:
                    if current.strftime('%A').lower() == sched.day:
                        DoctorDateSlot.objects.get_or_create(
                            schedule=sched,
                            date=current,
                            defaults={'max_patients': sched.max_patients, 'is_approved': True}
                        )
                    current += datetime.timedelta(days=1)

            locations = doctor.practice_locations.filter(is_active=True)
            locations_data = list(PracticeLocationSerializer(locations, many=True).data)

            slots = DoctorDateSlot.objects.filter(
                schedule__doctor=doctor,
                date__gte=today,
            ).exclude(
                status='cancelled'
            ).select_related(
                'schedule', 'schedule__practice_location', 'schedule__hospital'
            ).prefetch_related('bookings').order_by('date', 'schedule__start')
            slots_data = DoctorDateSlotSerializer(slots, many=True).data

            # Match slots to locations by practice_location FK ID first, then hospital name
            for loc in locations_data:
                loc_id = int(loc['id'])
                loc_name_lower = loc['name'].lower()
                matched = []
                for s in slots_data:
                    pl_id = s.get('practice_location_id')
                    hn = (s.get('hospital_name') or '').lower()
                    if pl_id and int(pl_id) == loc_id:
                        matched.append(s)
                    elif not pl_id and hn and (hn in loc_name_lower or loc_name_lower in hn):
                        matched.append(s)
                loc['slots'] = matched

            # Slots that didn't match any location
            matched_ids = {s['id'] for loc in locations_data for s in loc['slots']}
            unmatched = [s for s in slots_data if s['id'] not in matched_ids]
            if unmatched:
                # If only one location exists, assign all unmatched slots to it
                if len(locations_data) == 1:
                    locations_data[0]['slots'].extend(unmatched)
                else:
                    locations_data.append({
                        'id': None,
                        'name': 'General / Other Locations',
                        'type': 'other',
                        'address': None,
                        'city': None,
                        'contact_number': None,
                        'latitude': None,
                        'longitude': None,
                        'is_active': True,
                        'slots': unmatched,
                    })

            # Don't cache — booking counts change live
            return Response(APIResponse.success(f"{tab_name} tab data retrieved", "data", {'practice_locations': locations_data}))
        elif tab_name == 'affiliations':
            from profiles.serializers import HospitalSerializer, QualificationSerializer, SpecializationSerializer, SubSpecializationSerializer
            data = {
                'hospitals_detail': HospitalSerializer(doctor.hospital_affiliations.all(), many=True).data,
                'qualifications_detail': QualificationSerializer(doctor.qualifications.all(), many=True).data,
                'specialization_detail': SpecializationSerializer(doctor.specialization).data if doctor.specialization else None,
                'sub_specialization_detail': SubSpecializationSerializer(doctor.sub_specialization).data if doctor.sub_specialization else None,
                'license_number': doctor.license_number,
                'years_of_experience': doctor.years_of_experience,
            }
        elif tab_name == 'schedule':
            from profiles.serializers import DoctorSchedulingSerializer
            data = {'schedules': DoctorSchedulingSerializer(doctor.schedules.filter(is_active=True), many=True).data}
        elif tab_name == 'stats':
            from profiles.serializers import DoctorStatsSerializer
            data = {'evaluation': DoctorStatsSerializer(doctor.evaluation).data if hasattr(doctor, 'evaluation') and doctor.evaluation else None}

        CacheManager.SetCache(cache_key, data, CacheTTL.MEDIUM)
        return Response(APIResponse.success(f"{tab_name} tab data retrieved", "data", data))

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='available-slots')
    def available_slots(self, request, pk=None):
        doctor = self.get_object()
        from django.utils import timezone
        from django.db.models import F
        today = timezone.localtime(timezone.now()).date()
        slots = DoctorDateSlot.objects.filter(
            schedule__doctor=doctor,
            date__gte=today,
            status="open",
            is_approved=True,
            bookings_count__lt=F('max_patients')
        ).order_by('date', 'schedule__start')
        serializer = DoctorDateSlotSerializer(slots, many=True)
        return Response(APIResponse.success("Available slots retrieved", "slots", serializer.data))


class PracticeLocationViewSet(viewsets.ModelViewSet):
    serializer_class = PracticeLocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.request.query_params.get("doctor")
        if doctor_id:
            return PracticeLocation.objects.filter(doctor_id=doctor_id, is_active=True)
            
        try:
            from profiles.models import Doctor
            doctor = Doctor.objects.get(user=self.request.user)
            return PracticeLocation.objects.filter(doctor=doctor)
        except Doctor.DoesNotExist:
            return PracticeLocation.objects.filter(is_active=True)

    def perform_create(self, serializer):
        from profiles.models import Doctor
        doctor = Doctor.objects.get(user=self.request.user)
        serializer.save(doctor=doctor)


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
    search_fields = [
        'first_name', 'last_name', 'address',
        'division__division_name_eng', 'division__division_name_bn',
        'district__district_name_eng', 'district__district_name_bn',
        'upozila__upozila_name_eng', 'upozila__upoila_name_bn',
    ]

    def get_queryset(self):
        return BloodDonor.objects.select_related('user', 'division', 'district', 'upozila').prefetch_related('donation_posts').filter(is_active=True, user__is_blocked=False)

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

    @action(detail=False, methods=['post'], permission_classes=[IsBloodDonorUser], url_path='toggle-active')
    def toggle_active(self, request):
        """Blood donor can activate/deactivate their own profile visibility."""
        donor = BloodDonor.objects.filter(user=request.user).first()
        if not donor:
            return Response(APIResponse.error("Blood donor profile not found"), status=status.HTTP_404_NOT_FOUND)
        donor.is_active = not donor.is_active
        donor.save(update_fields=['is_active'])
        state = 'active' if donor.is_active else 'inactive'
        return Response(APIResponse.success(f"Profile is now {state}.", "is_active", donor.is_active))

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
        return AmbulanceProfile.objects.select_related('user', 'division', 'district', 'upozila').filter(is_active=True, user__is_blocked=False)

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

    @action(detail=False, methods=['post'], permission_classes=[IsAmbulanceUser], url_path='toggle-active')
    def toggle_active(self, request):
        """Ambulance owner can activate/deactivate their own profile visibility."""
        ambulance = AmbulanceProfile.objects.filter(user=request.user).first()
        if not ambulance:
            return Response(APIResponse.error("Ambulance profile not found"), status=status.HTTP_404_NOT_FOUND)
        ambulance.is_active = not ambulance.is_active
        ambulance.save(update_fields=['is_active'])
        state = 'active' if ambulance.is_active else 'inactive'
        return Response(APIResponse.success(f"Profile is now {state}.", "is_active", ambulance.is_active))


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
        return PharmacyProfile.objects.select_related('user', 'division', 'district', 'upozila').filter(is_active=True, user__is_blocked=False)

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

    @action(detail=False, methods=['post'], permission_classes=[IsPharmacyUser], url_path='toggle-active')
    def toggle_active(self, request):
        """Pharmacy owner can activate/deactivate their own profile visibility."""
        pharmacy = PharmacyProfile.objects.filter(user=request.user).first()
        if not pharmacy:
            return Response(APIResponse.error("Pharmacy profile not found"), status=status.HTTP_404_NOT_FOUND)
        pharmacy.is_active = not pharmacy.is_active
        pharmacy.save(update_fields=['is_active'])
        state = 'active' if pharmacy.is_active else 'inactive'
        return Response(APIResponse.success(f"Profile is now {state}.", "is_active", pharmacy.is_active))


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
    ordering = ['-created', '-id']

    def get_queryset(self):
        return PharmacyMedicine.objects.select_related('pharmacy').filter(pharmacy__is_active=True, pharmacy__user__is_blocked=False).order_by('-created', '-id')

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

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'pharmacy':
            return Response(APIResponse.error("Only registered pharmacies can edit medicines"), status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if instance.pharmacy.user != request.user:
            return Response(APIResponse.error("You can only edit medicines belonging to your pharmacy"), status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(APIResponse.success("Medicine updated successfully", "medicine", serializer.data))

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'pharmacy':
            return Response(APIResponse.error("Only registered pharmacies can delete medicines"), status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if instance.pharmacy.user != request.user:
            return Response(APIResponse.error("You can only delete medicines belonging to your pharmacy"), status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(APIResponse.success("Medicine deleted successfully"), status=status.HTTP_200_OK)


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
        return DiagnosticProfile.objects.select_related('user', 'division', 'district', 'upozila').filter(is_active=True, user__is_blocked=False)

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

    @action(detail=False, methods=['post'], permission_classes=[IsDiagnosticUser], url_path='toggle-active')
    def toggle_active(self, request):
        """Diagnostic center owner can activate/deactivate their own profile visibility."""
        diagnostic = DiagnosticProfile.objects.filter(user=request.user).first()
        if not diagnostic:
            return Response(APIResponse.error("Diagnostic profile not found"), status=status.HTTP_404_NOT_FOUND)
        diagnostic.is_active = not diagnostic.is_active
        diagnostic.save(update_fields=['is_active'])
        state = 'active' if diagnostic.is_active else 'inactive'
        return Response(APIResponse.success(f"Profile is now {state}.", "is_active", diagnostic.is_active))


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
    ordering = ['-created', '-id']

    def get_queryset(self):
        return DiagnosticTest.objects.select_related('diagnostic').order_by('-created', '-id')

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

    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'diagnostic':
            return Response(APIResponse.error("Only registered diagnostic centers can edit tests"), status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if instance.diagnostic.user != request.user:
            return Response(APIResponse.error("You can only edit tests belonging to your center"), status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(APIResponse.success("Diagnostic test updated successfully", "test", serializer.data))

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.user_type != 'diagnostic':
            return Response(APIResponse.error("Only registered diagnostic centers can delete tests"), status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if instance.diagnostic.user != request.user:
            return Response(APIResponse.error("You can only delete tests belonging to your center"), status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(APIResponse.success("Diagnostic test deleted successfully"), status=status.HTTP_200_OK)


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

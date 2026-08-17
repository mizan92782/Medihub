from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F

from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination
from profiles.models.doctor_prof_mod import Doctor, DoctorStats
from interactions.models.user_docotor_interaction import (
    UserDoctorInteractionFollwDoctor,
    UserDoctorInteractionAskQuestion,
    UserDoctorInteractionProfileShow,
)
from interactions.serializers import (
    DoctorFollowSerializer,
    DoctorAskQuestionSerializer,
    DoctorProfileShowSerializer,
)


class DoctorFollowViewSet(viewsets.ModelViewSet):
    """
    ViewSet to follow or unfollow doctors.
    """
    serializer_class = DoctorFollowSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return UserDoctorInteractionFollwDoctor.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_follow(self, request):
        doctor_id = request.data.get('doctor')
        if not doctor_id:
            return Response(APIResponse.error("doctor field is required"), status=status.HTTP_400_BAD_REQUEST)
        doctor = Doctor.objects.filter(pk=doctor_id).first()
        if not doctor:
            return Response(APIResponse.error("Doctor not found"), status=status.HTTP_404_NOT_FOUND)

        interaction, created = UserDoctorInteractionFollwDoctor.objects.get_or_create(
            user=request.user, doctor=doctor,
            defaults={'follow': True}
        )
        stats, _ = DoctorStats.objects.get_or_create(doctor=doctor)
        if not created:
            interaction.follow = not interaction.follow
            interaction.save()
            if interaction.follow:
                stats.total_followers += 1
            else:
                stats.total_followers = max(0, stats.total_followers - 1)
        else:
            stats.total_followers += 1
        stats.save()

        serializer = self.get_serializer(interaction)
        return Response(APIResponse.success("Follow status updated", "follow", serializer.data))


class DoctorQAViewSet(viewsets.ModelViewSet):
    """
    ViewSet for asking questions to doctors.
    """
    serializer_class = DoctorAskQuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['doctor', 'user']
    search_fields = ['question']

    def get_queryset(self):
        return UserDoctorInteractionAskQuestion.objects.select_related('user', 'doctor').all().order_by('-created_at')

    def perform_create(self, serializer):
        qa = serializer.save(user=self.request.user)
        if hasattr(qa.doctor, 'evaluation'):
            DoctorStats.objects.filter(doctor=qa.doctor).update(total_questions=F('total_questions') + 1)


class DoctorProfileTrackerView(viewsets.GenericViewSet):
    """
    Endpoint to log doctor profile views.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='track-view')
    def track_view(self, request):
        doctor_id = request.data.get('doctor')
        if not doctor_id:
            return Response(APIResponse.error("doctor is required"), status=status.HTTP_400_BAD_REQUEST)
        doctor = Doctor.objects.filter(pk=doctor_id).first()
        if not doctor:
            return Response(APIResponse.error("Doctor not found"), status=status.HTTP_404_NOT_FOUND)

        record = UserDoctorInteractionProfileShow.objects.create(user=request.user, doctor=doctor)
        DoctorStats.objects.filter(doctor=doctor).update(total_profile_views=F('total_profile_views') + 1)
        return Response(APIResponse.success("Profile view tracked", "tracker", DoctorProfileShowSerializer(record).data))

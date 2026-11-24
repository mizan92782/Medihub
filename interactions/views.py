from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
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
from interactions.models.user_follow import UserFollow
from interactions.serializers import (
    DoctorFollowSerializer,
    DoctorAskQuestionSerializer,
    DoctorProfileShowSerializer,
)
from authentication.models import User


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

        from django.db import transaction

        with transaction.atomic():
            interaction, created = UserDoctorInteractionFollwDoctor.objects.select_for_update().get_or_create(
                user=request.user, doctor=doctor,
                defaults={'follow': True}
            )
            DoctorStats.objects.get_or_create(doctor=doctor)
            if not created:
                interaction.follow = not interaction.follow
                interaction.save(update_fields=['follow'])
                if interaction.follow:
                    DoctorStats.objects.filter(doctor=doctor).update(total_followers=F('total_followers') + 1)
                else:
                    DoctorStats.objects.filter(doctor=doctor, total_followers__gt=0).update(total_followers=F('total_followers') - 1)
            else:
                DoctorStats.objects.filter(doctor=doctor).update(total_followers=F('total_followers') + 1)

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


class UserFollowViewSet(viewsets.ViewSet):
    """
    Generic user-to-user follow/unfollow with notifications.
    POST /interactions/user-follow/toggle/  { "user_id": <id> }
    GET  /interactions/user-follow/followers/
    GET  /interactions/user-follow/following/
    GET  /interactions/user-follow/status/?user_id=<id>
    """
    permission_classes = [IsAuthenticated]

    def _get_author_name(self, user):
        try:
            if hasattr(user, 'doctor') and user.doctor:
                d = user.doctor
                return f"Dr. {d.first_name} {d.last_name}".strip()
            if hasattr(user, 'profile') and user.profile:
                p = user.profile
                return f"{p.first_name} {p.last_name}".strip() or user.email.split('@')[0]
            if hasattr(user, 'blood_donor') and user.blood_donor:
                d = user.blood_donor
                return f"{d.first_name} {d.last_name}".strip()
            if hasattr(user, 'ambulance') and user.ambulance:
                return user.ambulance.owner_name or user.email.split('@')[0]
            if hasattr(user, 'pharmacy') and user.pharmacy:
                return user.pharmacy.pharmacy_name or user.email.split('@')[0]
            if hasattr(user, 'diagnostic') and user.diagnostic:
                return user.diagnostic.diagnostic_name or user.email.split('@')[0]
        except Exception:
            pass
        return user.email.split('@')[0]

    @action(detail=False, methods=['post'], url_path='toggle')
    def toggle_follow(self, request):
        target_id = request.data.get('user_id')
        if not target_id:
            return Response(APIResponse.error("user_id is required"), status=status.HTTP_400_BAD_REQUEST)

        target = User.objects.filter(pk=target_id).first()
        if not target:
            return Response(APIResponse.error("User not found"), status=status.HTTP_404_NOT_FOUND)

        if target == request.user:
            return Response(APIResponse.error("You cannot follow yourself"), status=status.HTTP_400_BAD_REQUEST)

        follow_obj = UserFollow.objects.filter(follower=request.user, following=target).first()

        if follow_obj:
            follow_obj.delete()
            followed = False
        else:
            UserFollow.objects.create(follower=request.user, following=target)
            followed = True
            # Notify the followed user
            from notification.servcies import AppNotificationService, PushNotification
            follower_name = self._get_author_name(request.user)
            AppNotificationService.create_notification(
                user=target,
                title="New Follower",
                message=f"{follower_name} started following you.",
                post_type="follow",
            )
            PushNotification.send_to_user(
                user=target,
                title="New Follower 🔔",
                body=f"{follower_name} started following you.",
            )

        followers_count = UserFollow.objects.filter(following=target).count()
        following_count = UserFollow.objects.filter(follower=target).count()

        return Response(APIResponse.success(
            "Follow status updated",
            "follow",
            {
                "followed": followed,
                "target_user_id": target.id,
                "followers_count": followers_count,
                "following_count": following_count,
            }
        ))

    @action(detail=False, methods=['get'], url_path='status', permission_classes=[AllowAny])
    def follow_status(self, request):
        target_id = request.query_params.get('user_id')
        if not target_id:
            return Response(APIResponse.error("user_id is required"), status=status.HTTP_400_BAD_REQUEST)
        is_following = (
            UserFollow.objects.filter(follower=request.user, following_id=target_id).exists()
            if request.user.is_authenticated else False
        )
        followers_count = UserFollow.objects.filter(following_id=target_id).count()
        following_count = UserFollow.objects.filter(follower_id=target_id).count()
        return Response(APIResponse.success("Follow status", "status", {
            "is_following": is_following,
            "followers_count": followers_count,
            "following_count": following_count,
        }))

    @action(detail=False, methods=['get'], url_path='followers', permission_classes=[AllowAny])
    def list_followers(self, request):
        user_id = request.query_params.get('user_id') or (request.user.id if request.user.is_authenticated else None)
        if not user_id:
            return Response(APIResponse.error("user_id required"), status=status.HTTP_400_BAD_REQUEST)
        qs = UserFollow.objects.filter(following_id=user_id).select_related('follower')
        data = [{"user_id": f.follower.id, "email": f.follower.email, "name": self._get_author_name(f.follower), "since": f.created_at} for f in qs]
        return Response(APIResponse.success("Followers list", "followers", data))

    @action(detail=False, methods=['get'], url_path='following', permission_classes=[AllowAny])
    def list_following(self, request):
        user_id = request.query_params.get('user_id') or (request.user.id if request.user.is_authenticated else None)
        if not user_id:
            return Response(APIResponse.error("user_id required"), status=status.HTTP_400_BAD_REQUEST)
        qs = UserFollow.objects.filter(follower_id=user_id).select_related('following')
        data = [{"user_id": f.following.id, "email": f.following.email, "name": self._get_author_name(f.following), "since": f.created_at} for f in qs]
        return Response(APIResponse.success("Following list", "following", data))

    @action(detail=False, methods=['get'], url_path='my-counts')
    def my_counts(self, request):
        followers = UserFollow.objects.filter(following=request.user).count()
        following = UserFollow.objects.filter(follower=request.user).count()
        return Response(APIResponse.success("My follow counts", "counts", {
            "followers": followers,
            "following": following,
        }))

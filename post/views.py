from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
import time

from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination
from core.permissions import IsOwnerOrReadOnly
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.equipment_sell_mod import EquipmentSellPost
from post.models.medicine_post_mod import MedicinePost
from post.models.general_post_mod import GeneralPost
from post.models.ambulance_need_mod import AmbulanceNeedPost
from post.models.post_interactions_mod import PostLike, PostComment, PostShare
from post.models.post_image_mod import PostImage
from profiles.models import BloodDonationPost
from profiles.models.blood_donor_mod import BloodDonor
from interactions.models.user_follow import UserFollow
from notification.servcies import AppNotificationService

from post.serializers import (
    BloodNeedPostSerializer,
    MedicineNeedPostSerializer,
    EquipmentNeedPostSerializer,
    EquipmentSellPostSerializer,
    MedicinePostSerializer,
    GeneralPostSerializer,
    AmbulanceNeedPostSerializer,
    PostLikeSerializer,
    PostCommentSerializer,
    PostShareSerializer,
    PostImageSerializer,
)
from donor.serializers import BloodDonationPostSerializer


def _notify_followers_new_post(author, post_type, post_id, summary):
    """Delegate follower notifications to background Celery worker for fast API response."""
    try:
        from post.tasks import notify_followers_new_post_task
        notify_followers_new_post_task.delay(author.id, post_type, post_id, summary)
    except Exception:
        pass


class BloodNeedPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Blood Need Posts CRUD and filtering.
    """
    serializer_class = BloodNeedPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['blood_group', 'urgency', 'status', 'division', 'district', 'upozila']
    search_fields = ['patient_name', 'hospital_name', 'hospital_address', 'description']
    ordering_fields = ['created', 'needed_date', 'urgency']

    def get_queryset(self):
        return BloodNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        is_urgent = serializer.validated_data.get('urgency') in ('critical', 'high')
        post = serializer.save(user=self.request.user, is_urgent_post=is_urgent)
        if is_urgent and post.district:
            from post.tasks import send_urgent_blood_notifications
            send_urgent_blood_notifications.delay(post.id)
        _notify_followers_new_post(self.request.user, 'blood_need', post.id, f"Blood Need: {post.blood_group}")

    @action(detail=False, methods=['get'], url_path='urgent', permission_classes=[AllowAny])
    def urgent_posts(self, request):
        posts = list(BloodNeedPost.objects.filter(
            is_urgent_post=True,
            status='open'
        ).select_related('user', 'division', 'district', 'upozila').order_by('-created')[:50])
        
        if not posts:
            return Response(APIResponse.success("Urgent blood posts", "posts", []))

        ct = ContentType.objects.get_for_model(BloodNeedPost)
        post_ids = [p.id for p in posts]

        likes_map = dict(
            PostLike.objects.filter(content_type=ct, object_id__in=post_ids)
            .values('object_id').annotate(count=Count('id'))
            .values_list('object_id', 'count')
        )
        comments_map = dict(
            PostComment.objects.filter(content_type=ct, object_id__in=post_ids)
            .values('object_id').annotate(count=Count('id'))
            .values_list('object_id', 'count')
        )
        user_liked_set = set()
        if request.user.is_authenticated:
            user_liked_set = set(
                PostLike.objects.filter(content_type=ct, object_id__in=post_ids, user=request.user)
                .values_list('object_id', flat=True)
            )

        data = []
        for post in posts:
            item = BloodNeedPostSerializer(post).data
            item['likes_count'] = likes_map.get(post.id, 0)
            item['comments_count'] = comments_map.get(post.id, 0)
            item['user_has_liked'] = post.id in user_liked_set
            data.append(item)
        return Response(APIResponse.success("Urgent blood posts", "posts", data))

    @action(detail=True, methods=['post'], url_path='fulfill')
    def mark_fulfilled(self, request, pk=None):
        post = self.get_object()
        post.status = 'fulfilled'
        post.save()
        return Response(APIResponse.success("Post marked as fulfilled", "post", self.get_serializer(post).data))

    @action(detail=True, methods=['post'], url_path='close')
    def mark_closed(self, request, pk=None):
        post = self.get_object()
        post.status = 'closed'
        post.save()
        return Response(APIResponse.success("Post marked as closed", "post", self.get_serializer(post).data))


class MedicineNeedPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Medicine Need Posts CRUD and filtering.
    """
    serializer_class = MedicineNeedPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['urgency', 'status', 'division', 'district', 'upozila']
    search_fields = ['medicine_name', 'description', 'address']
    ordering_fields = ['created', 'urgency']

    def get_queryset(self):
        return MedicineNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        _notify_followers_new_post(self.request.user, 'medicine_need', post.id, f"Medicine Need: {post.medicine_name}")

    @action(detail=True, methods=['post'], url_path='fulfill')
    def mark_fulfilled(self, request, pk=None):
        post = self.get_object()
        post.status = 'fulfilled'
        post.save()
        return Response(APIResponse.success("Post marked as fulfilled", "post", self.get_serializer(post).data))

    @action(detail=True, methods=['post'], url_path='close')
    def mark_closed(self, request, pk=None):
        post = self.get_object()
        post.status = 'closed'
        post.save()
        return Response(APIResponse.success("Post marked as closed", "post", self.get_serializer(post).data))


class EquipmentNeedPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Equipment Need Posts CRUD and filtering.
    """
    serializer_class = EquipmentNeedPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['condition', 'urgency', 'status', 'division', 'district', 'upozila']
    search_fields = ['equipment_name', 'description', 'address']
    ordering_fields = ['created', 'urgency']

    def get_queryset(self):
        return EquipmentNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        _notify_followers_new_post(self.request.user, 'equipment_need', post.id, f"Equipment Need: {post.equipment_name}")

    @action(detail=True, methods=['post'], url_path='fulfill')
    def mark_fulfilled(self, request, pk=None):
        post = self.get_object()
        post.status = 'fulfilled'
        post.save()
        return Response(APIResponse.success("Post marked as fulfilled", "post", self.get_serializer(post).data))

    @action(detail=True, methods=['post'], url_path='close')
    def mark_closed(self, request, pk=None):
        post = self.get_object()
        post.status = 'closed'
        post.save()
        return Response(APIResponse.success("Post marked as closed", "post", self.get_serializer(post).data))


class GeneralPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for General Posts CRUD and filtering.
    """
    serializer_class = GeneralPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'division', 'district', 'upozila']
    search_fields = ['title', 'content']
    ordering_fields = ['created']

    def get_queryset(self):
        return GeneralPost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        _notify_followers_new_post(self.request.user, 'general', post.id, post.title)

    @action(detail=True, methods=['post'], url_path='fulfill')
    def mark_fulfilled(self, request, pk=None):
        post = self.get_object()
        post.status = 'fulfilled'
        post.save()
        return Response(APIResponse.success("Post marked as fulfilled", "post", self.get_serializer(post).data))

    @action(detail=True, methods=['post'], url_path='close')
    def mark_closed(self, request, pk=None):
        post = self.get_object()
        post.status = 'closed'
        post.save()
        return Response(APIResponse.success("Post marked as closed", "post", self.get_serializer(post).data))


class AmbulanceNeedPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ambulance Need Posts CRUD and filtering.
    """
    serializer_class = AmbulanceNeedPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['ambulance_type', 'urgency', 'status', 'division', 'district', 'upozila']
    search_fields = ['address', 'description', 'contact_number']
    ordering_fields = ['created', 'needed_date', 'urgency']

    def get_queryset(self):
        return AmbulanceNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        _notify_followers_new_post(self.request.user, 'ambulance_need', post.id, f"Ambulance Need: {post.ambulance_type}")

    @action(detail=True, methods=['post'], url_path='fulfill')
    def mark_fulfilled(self, request, pk=None):
        post = self.get_object()
        post.status = 'fulfilled'
        post.save()
        return Response(APIResponse.success("Post marked as fulfilled", "post", self.get_serializer(post).data))

    @action(detail=True, methods=['post'], url_path='close')
    def mark_closed(self, request, pk=None):
        post = self.get_object()
        post.status = 'closed'
        post.save()
        return Response(APIResponse.success("Post marked as closed", "post", self.get_serializer(post).data))


class EquipmentSellPostViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentSellPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['condition', 'status', 'division', 'district', 'upozila']
    search_fields = ['equipment_name', 'description', 'address']
    ordering_fields = ['created']

    def get_queryset(self):
        return EquipmentSellPost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        _notify_followers_new_post(self.request.user, 'equipment_sell', post.id, f"Equipment Sell: {post.equipment_name}")


class MedicinePostViewSet(viewsets.ModelViewSet):
    serializer_class = MedicinePostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['listing_type', 'status', 'division', 'district', 'upozila']
    search_fields = ['medicine_name', 'description', 'address']
    ordering_fields = ['created']

    def get_queryset(self):
        return MedicinePost.objects.select_related('user', 'division', 'district', 'upozila').all()

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)
        _notify_followers_new_post(self.request.user, 'medicine', post.id, f"Medicine: {post.medicine_name}")


class PostImageUploadView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['post'], url_path='upload')
    def upload_images(self, request):
        post_type = request.data.get('post_type')
        post_id = request.data.get('post_id')
        images = request.FILES.getlist('images')

        if not post_type or not post_id or not images:
            return Response(APIResponse.error('post_type, post_id, and images are required'), status=400)

        model_map = {
            'blood_need': BloodNeedPost,
            'medicine_need': MedicineNeedPost,
            'equipment_need': EquipmentNeedPost,
            'equipment_sell': EquipmentSellPost,
            'medicine': MedicinePost,
            'ambulance_need': AmbulanceNeedPost,
            'general': GeneralPost,
            'blood_donation': BloodDonationPost,
        }
        model_class = model_map.get(post_type)
        if not model_class:
            return Response(APIResponse.error('Invalid post_type'), status=400)

        post_instance = model_class.objects.filter(id=post_id).first()
        if not post_instance:
            return Response(APIResponse.error('Post not found'), status=404)

        ct = ContentType.objects.get_for_model(model_class)
        created_images = []
        for i, img in enumerate(images):
            pi = PostImage.objects.create(content_type=ct, object_id=post_id, image=img, order=i)
            created_images.append(PostImageSerializer(pi).data)

        return Response(APIResponse.success('Images uploaded', 'images', created_images))


def bump_feed_version(*args, **kwargs):
    try:
        cache.incr('community_feed_version')
    except Exception:
        cache.set('community_feed_version', int(time.time() * 1000), timeout=86400 * 30)

for _model in [BloodNeedPost, MedicineNeedPost, EquipmentNeedPost, EquipmentSellPost,
               MedicinePost, GeneralPost, AmbulanceNeedPost, BloodDonationPost,
               PostLike, PostComment, PostShare, UserFollow]:
    post_save.connect(bump_feed_version, sender=_model)
    post_delete.connect(bump_feed_version, sender=_model)


class PostInteractionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_post_model_and_content_type(self, post_type, post_id):
        mapping = {
            'blood_need': (BloodNeedPost, 'bloodneedpost'),
            'medicine_need': (MedicineNeedPost, 'medicineneedpost'),
            'equipment_need': (EquipmentNeedPost, 'equipmentneedpost'),
            'equipment_sell': (EquipmentSellPost, 'equipmentsellpost'),
            'medicine': (MedicinePost, 'medicinepost'),
            'general': (GeneralPost, 'generalpost'),
            'ambulance_need': (AmbulanceNeedPost, 'ambulanceneedpost'),
            'blood_donation': (BloodDonationPost, 'blooddonationpost')
        }
        if post_type not in mapping:
            return None, None, None
        model_class, ct_model_name = mapping[post_type]
        ct = ContentType.objects.get_for_model(model_class)
        post_instance = model_class.objects.filter(id=post_id).first()
        return post_instance, ct, model_class

    @action(detail=False, methods=['post'], url_path='like')
    def like_post(self, request):
        post_type = request.data.get('post_type')
        post_id = request.data.get('post_id')
        if not post_type or not post_id:
            return Response(APIResponse.error("post_type and post_id are required"), status=status.HTTP_400_BAD_REQUEST)
        
        post_instance, ct, _ = self._get_post_model_and_content_type(post_type, post_id)
        if not post_instance:
            return Response(APIResponse.error("Post not found"), status=status.HTTP_404_NOT_FOUND)
        
        like, created = PostLike.objects.get_or_create(
            user=request.user,
            content_type=ct,
            object_id=post_id
        )
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
            
        total_likes = PostLike.objects.filter(content_type=ct, object_id=post_id).count()
        bump_feed_version()
        return Response(APIResponse.success("Post like status updated", "like", {"liked": liked, "total_likes": total_likes}))

    @action(detail=False, methods=['post'], url_path='comment')
    def comment_post(self, request):
        post_type = request.data.get('post_type')
        post_id = request.data.get('post_id')
        content = request.data.get('content')
        if not post_type or not post_id or not content:
            return Response(APIResponse.error("post_type, post_id, and content are required"), status=status.HTTP_400_BAD_REQUEST)
        
        post_instance, ct, _ = self._get_post_model_and_content_type(post_type, post_id)
        if not post_instance:
            return Response(APIResponse.error("Post not found"), status=status.HTTP_404_NOT_FOUND)
        
        comment = PostComment.objects.create(
            user=request.user,
            content_type=ct,
            object_id=post_id,
            content=content
        )
        bump_feed_version()
        return Response(APIResponse.success("Comment added successfully", "comment", PostCommentSerializer(comment).data))

    @action(detail=False, methods=['get'], url_path='comments', permission_classes=[AllowAny])
    def get_comments(self, request):
        post_type = request.query_params.get('post_type')
        post_id = request.query_params.get('post_id')
        if not post_type or not post_id:
            return Response(APIResponse.error("post_type and post_id are required"), status=status.HTTP_400_BAD_REQUEST)
        
        post_instance, ct, _ = self._get_post_model_and_content_type(post_type, post_id)
        if not post_instance:
            return Response(APIResponse.error("Post not found"), status=status.HTTP_404_NOT_FOUND)
            
        comments = PostComment.objects.filter(content_type=ct, object_id=post_id).order_by('created_at')
        serializer = PostCommentSerializer(comments, many=True)
        return Response(APIResponse.success("Comments retrieved successfully", "comments", serializer.data))

    @action(detail=False, methods=['post'], url_path='share')
    def share_post(self, request):
        post_type = request.data.get('post_type')
        post_id = request.data.get('post_id')
        if not post_type or not post_id:
            return Response(APIResponse.error("post_type and post_id are required"), status=status.HTTP_400_BAD_REQUEST)
            
        post_instance, ct, _ = self._get_post_model_and_content_type(post_type, post_id)
        if not post_instance:
            return Response(APIResponse.error("Post not found"), status=status.HTTP_404_NOT_FOUND)
            
        PostShare.objects.create(user=request.user, content_type=ct, object_id=post_id)
        total_shares = PostShare.objects.filter(content_type=ct, object_id=post_id).count()
        bump_feed_version()
        return Response(APIResponse.success("Share logged successfully", "share", {"total_shares": total_shares}))


class PostFeedViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        user = request.user
        search = request.query_params.get('search', '').strip().lower()
        post_type_filter = request.query_params.get('post_type', 'all')
        sort_by = request.query_params.get('sort', 'recommended')  # recommended (default) | newest | urgent | most_liked | most_commented | oldest
        user_id_param = request.query_params.get('user_id')

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (TypeError, ValueError):
            page = 1
        try:
            page_size = max(1, min(50, int(request.query_params.get('page_size', 10))))
        except (TypeError, ValueError):
            page_size = 10

        # Cache check
        v = cache.get('community_feed_version') or 1
        user_cache_id = user.id if user and user.is_authenticated else 'anon'
        cache_key = f"feed_v{v}_{user_cache_id}_{post_type_filter}_{sort_by}_{page}_{page_size}_{search}_{user_id_param}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # Preload User Preferences for Recommendation Scoring
        user_following_ids = set()
        user_district_id = None
        user_division_id = None
        user_blood_group = None
        user_type = getattr(user, 'user_type', None)

        if user and user.is_authenticated:
            try:
                user_following_ids = set(UserFollow.objects.filter(follower=user).values_list('following_id', flat=True))
            except Exception:
                pass

            try:
                if hasattr(user, 'profile') and user.profile:
                    user_district_id = user.profile.district_id
                    user_division_id = user.profile.division_id
                elif hasattr(user, 'blood_donor') and user.blood_donor:
                    user_district_id = user.blood_donor.district_id
                    user_division_id = user.blood_donor.division_id
                    user_blood_group = user.blood_donor.blood_group
                elif hasattr(user, 'doctor') and user.doctor:
                    user_district_id = user.doctor.district_id
                    user_division_id = user.doctor.division_id
                elif hasattr(user, 'ambulance') and user.ambulance:
                    user_district_id = user.ambulance.district_id
                    user_division_id = user.ambulance.division_id
            except Exception:
                pass

        feed_items = []

        def process_model(model_cls, p_type, serializer_cls, is_donation=False):
            if post_type_filter != 'all' and post_type_filter != p_type:
                return

            select_fields = ['division', 'district', 'upozila']
            if is_donation:
                select_fields.append('donor__user')
            else:
                select_fields.append('user')

            qs = model_cls.objects.select_related(*select_fields).all()

            ct = ContentType.objects.get_for_model(model_cls)

            # Bulk aggregate likes, comments, shares
            likes_map = dict(
                PostLike.objects.filter(content_type=ct)
                .values('object_id')
                .annotate(c=Count('id'))
                .values_list('object_id', 'c')
            )
            comments_map = dict(
                PostComment.objects.filter(content_type=ct)
                .values('object_id')
                .annotate(c=Count('id'))
                .values_list('object_id', 'c')
            )
            shares_map = dict(
                PostShare.objects.filter(content_type=ct)
                .values('object_id')
                .annotate(c=Count('id'))
                .values_list('object_id', 'c')
            )
            user_liked_set = set()
            if user and user.is_authenticated:
                user_liked_set = set(
                    PostLike.objects.filter(content_type=ct, user=user)
                    .values_list('object_id', flat=True)
                )

            for post in qs:
                email = ""
                u_id = None
                author_user = None

                if is_donation:
                    if post.donor and post.donor.user:
                        email = post.donor.user.email
                        u_id = post.donor.user.id
                        author_user = post.donor.user
                else:
                    if post.user:
                        email = post.user.email
                        u_id = post.user.id
                        author_user = post.user

                if user_id_param and str(u_id) != str(user_id_param):
                    continue

                author_name = email.split("@")[0] if email else "User"
                author_avatar = None
                author_role = getattr(author_user, 'user_type', 'regular') if author_user else 'regular'
                author_profile_id = u_id
                author_route = f"/user/{u_id}" if u_id else "/community"

                if author_user:
                    try:
                        # Check specific professional/donor roles first to give priority over default profile
                        if author_role == 'blood_donor' or getattr(author_user, 'blood_donor', None):
                            donor = getattr(author_user, 'blood_donor', None)
                            if donor:
                                author_role = 'blood_donor'
                                author_profile_id = donor.id
                                author_route = f"/donor-profile/{donor.id}"
                                author_name = f"{donor.first_name} {donor.last_name}".strip() or author_name
                                author_avatar = donor.profile_dp.url if donor.profile_dp else None
                        elif author_role == 'doctor' or getattr(author_user, 'doctor', None):
                            doc = getattr(author_user, 'doctor', None)
                            if doc:
                                author_role = 'doctor'
                                author_profile_id = doc.id
                                author_route = f"/doctor-profile/{doc.id}"
                                author_name = f"Dr. {doc.first_name} {doc.last_name}".strip()
                                author_avatar = doc.profile_dp.url if doc.profile_dp else None
                        elif author_role == 'ambulance' or getattr(author_user, 'ambulance', None):
                            amb = getattr(author_user, 'ambulance', None)
                            if amb:
                                author_role = 'ambulance'
                                author_profile_id = amb.id
                                author_route = f"/ambulance-profile/{amb.id}"
                                author_name = amb.owner_name or author_name
                                author_avatar = amb.profile_dp.url if amb.profile_dp else None
                        elif author_role == 'pharmacy' or getattr(author_user, 'pharmacy', None):
                            ph = getattr(author_user, 'pharmacy', None)
                            if ph:
                                author_role = 'pharmacy'
                                author_profile_id = ph.id
                                author_route = f"/pharmacy-profile/{ph.id}"
                                author_name = ph.pharmacy_name or author_name
                                author_avatar = ph.profile_dp.url if ph.profile_dp else None
                        elif author_role == 'diagnostic' or getattr(author_user, 'diagnostic', None):
                            dg = getattr(author_user, 'diagnostic', None)
                            if dg:
                                author_role = 'diagnostic'
                                author_profile_id = dg.id
                                author_route = f"/diagnostic-profile/{dg.id}"
                                author_name = dg.diagnostic_name or author_name
                                author_avatar = dg.profile_dp.url if dg.profile_dp else None
                        elif hasattr(author_user, 'profile') and author_user.profile:
                            prof = author_user.profile
                            author_name = f"{prof.first_name} {prof.last_name}".strip() or author_name
                            author_avatar = prof.profile_dp.url if prof.profile_dp else None
                    except Exception:
                        pass

                details_data = serializer_cls(post).data
                likes_count = likes_map.get(post.id, 0)
                comments_count = comments_map.get(post.id, 0)
                shares_count = shares_map.get(post.id, 0)
                user_has_liked = post.id in user_liked_set

                # Search filter
                if search:
                    searchable = " ".join([
                        str(email),
                        str(author_name),
                        str(details_data.get('patient_name', '')),
                        str(details_data.get('medicine_name', '')),
                        str(details_data.get('equipment_name', '')),
                        str(details_data.get('title', '')),
                        str(details_data.get('content', '')),
                        str(details_data.get('blood_group', '')),
                        str(details_data.get('hospital_name', '')),
                        str(details_data.get('description', '')),
                        str(post.district.district_name_eng if post.district else ''),
                        str(post.division.division_name_eng if post.division else ''),
                    ]).lower()
                    if search not in searchable:
                        continue

                # Compute Dynamic Personalized Recommendation Score
                score = 0.0

                # 1. Following Boost:
                if u_id and u_id in user_following_ids:
                    score += 150.0

                # 2. Location Relevance:
                p_district_id = getattr(post, 'district_id', None)
                p_division_id = getattr(post, 'division_id', None)
                if user_district_id and p_district_id and user_district_id == p_district_id:
                    score += 60.0
                elif user_division_id and p_division_id and user_division_id == p_division_id:
                    score += 30.0

                # 3. User Role & Needs:
                if user_type == 'blood_donor' or getattr(user, 'is_blood_donor', False):
                    if p_type == 'blood_need':
                        score += 80.0
                        if user_blood_group and details_data.get('blood_group') == user_blood_group:
                            score += 40.0
                elif user_type == 'ambulance' and p_type == 'ambulance_need':
                    score += 80.0
                elif user_type in ['doctor', 'pharmacy'] and p_type in ['medicine_need', 'medicine']:
                    score += 60.0

                # 4. Urgency:
                p_urgency = str(getattr(post, 'urgency', 'medium')).lower()
                if p_urgency == 'critical':
                    score += 70.0
                elif p_urgency == 'high':
                    score += 40.0
                elif p_urgency == 'medium':
                    score += 15.0

                # 5. Engagement:
                score += (likes_count * 2.5) + (comments_count * 4.0) + (shares_count * 3.0)

                # 6. Freshness (Recency decay):
                created_ts = post.created.timestamp() if hasattr(post.created, 'timestamp') else 0
                hours_ago = max(0, (time.time() - created_ts) / 3600)
                freshness = max(0.0, 80.0 - (hours_ago * 0.8))
                score += freshness

                feed_items.append({
                    "id": post.id,
                    "user_email": email,
                    "user_id": u_id,
                    "author_name": author_name,
                    "author_avatar": author_avatar,
                    "author_role": author_role,
                    "author_profile_id": author_profile_id,
                    "author_route": author_route,
                    "post_type": p_type,
                    "created": post.created,
                    "urgency": getattr(post, 'urgency', 'medium'),
                    "status": getattr(post, 'status', 'open'),
                    "division_name": post.division.division_name_eng if post.division else None,
                    "district_name": post.district.district_name_eng if post.district else None,
                    "upozila_name": post.upozila.upozila_name_eng if post.upozila else None,
                    "likes_count": likes_count,
                    "comments_count": comments_count,
                    "shares_count": shares_count,
                    "user_has_liked": user_has_liked,
                    "details": details_data,
                    "score": round(score, 2),
                })

        process_model(BloodNeedPost, 'blood_need', BloodNeedPostSerializer)
        process_model(MedicineNeedPost, 'medicine_need', MedicineNeedPostSerializer)
        process_model(EquipmentNeedPost, 'equipment_need', EquipmentNeedPostSerializer)
        process_model(EquipmentSellPost, 'equipment_sell', EquipmentSellPostSerializer)
        process_model(MedicinePost, 'medicine', MedicinePostSerializer)
        process_model(GeneralPost, 'general', GeneralPostSerializer)
        process_model(AmbulanceNeedPost, 'ambulance_need', AmbulanceNeedPostSerializer)
        process_model(BloodDonationPost, 'blood_donation', BloodDonationPostSerializer, is_donation=True)

        URGENCY_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

        # Sorting
        if sort_by == 'recommended':
            feed_items.sort(key=lambda x: x['score'], reverse=True)
        elif sort_by == 'newest':
            feed_items.sort(key=lambda x: -x['created'].timestamp() if hasattr(x['created'], 'timestamp') else 0)
        elif sort_by == 'oldest':
            feed_items.sort(key=lambda x: x['created'].timestamp() if hasattr(x['created'], 'timestamp') else 0)
        elif sort_by == 'most_liked':
            feed_items.sort(key=lambda x: x['likes_count'], reverse=True)
        elif sort_by == 'most_commented':
            feed_items.sort(key=lambda x: x['comments_count'], reverse=True)
        elif sort_by == 'urgent':
            feed_items.sort(key=lambda x: (
                URGENCY_ORDER.get(str(x.get('urgency', 'medium')).lower(), 2),
                -x['created'].timestamp() if hasattr(x['created'], 'timestamp') else 0
            ))
        else:
            feed_items.sort(key=lambda x: x['score'], reverse=True)

        # Pagination: default 10 per page
        total_items = len(feed_items)
        total_pages = max(1, (total_items + page_size - 1) // page_size)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_items = feed_items[start_idx:end_idx]

        response_payload = {
            "success": True,
            "message": "Feed loaded successfully",
            "feed": paged_items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_items": total_items,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        }
        cache.set(cache_key, response_payload, timeout=60)
        return Response(response_payload)

    @action(detail=False, methods=['get'], url_path='single')
    def single_post(self, request):
        post_type = request.query_params.get('post_type')
        post_id = request.query_params.get('id') or request.query_params.get('post_id')
        if not post_type or not post_id:
            return Response(APIResponse.error("post_type and id are required"), status=status.HTTP_400_BAD_REQUEST)

        mapping = {
            'blood_need': (BloodNeedPost, BloodNeedPostSerializer),
            'medicine_need': (MedicineNeedPost, MedicineNeedPostSerializer),
            'equipment_need': (EquipmentNeedPost, EquipmentNeedPostSerializer),
            'equipment_sell': (EquipmentSellPost, EquipmentSellPostSerializer),
            'medicine': (MedicinePost, MedicinePostSerializer),
            'general': (GeneralPost, GeneralPostSerializer),
            'ambulance_need': (AmbulanceNeedPost, AmbulanceNeedPostSerializer),
            'blood_donation': (BloodDonationPost, BloodDonationPostSerializer),
        }
        if post_type not in mapping:
            return Response(APIResponse.error("Invalid post_type"), status=status.HTTP_400_BAD_REQUEST)

        model_class, serializer_class = mapping[post_type]
        select_fields = ['division', 'district', 'upozila']
        if post_type == 'blood_donation':
            select_fields.append('donor__user')
        else:
            select_fields.append('user')

        post = model_class.objects.select_related(*select_fields).filter(id=post_id).first()
        if not post:
            return Response(APIResponse.error("Post not found"), status=status.HTTP_404_NOT_FOUND)

        ct = ContentType.objects.get_for_model(model_class)
        likes = PostLike.objects.filter(content_type=ct, object_id=post.id)
        comments_count = PostComment.objects.filter(content_type=ct, object_id=post.id).count()
        shares_count = PostShare.objects.filter(content_type=ct, object_id=post.id).count()

        user = request.user
        user_has_liked = False
        if user and user.is_authenticated:
            user_has_liked = likes.filter(user=user).exists()

        email = ""
        user_id = None
        author_user = None
        if post_type == 'blood_donation':
            if post.donor and post.donor.user:
                email = post.donor.user.email
                user_id = post.donor.user.id
                author_user = post.donor.user
        else:
            if post.user:
                email = post.user.email
                user_id = post.user.id
                author_user = post.user

        author_name = email.split("@")[0] if email else "User"
        author_avatar = None
        author_role = getattr(author_user, 'user_type', 'regular') if author_user else 'regular'
        author_profile_id = user_id
        author_route = f"/user/{user_id}" if user_id else "/community"

        if author_user:
            try:
                if author_role == 'blood_donor' or getattr(author_user, 'blood_donor', None):
                    donor = getattr(author_user, 'blood_donor', None)
                    if donor:
                        author_role = 'blood_donor'
                        author_profile_id = donor.id
                        author_route = f"/donor-profile/{donor.id}"
                        author_name = f"{donor.first_name} {donor.last_name}".strip() or author_name
                        author_avatar = donor.profile_dp.url if donor.profile_dp else None
                elif author_role == 'doctor' or getattr(author_user, 'doctor', None):
                    doc = getattr(author_user, 'doctor', None)
                    if doc:
                        author_role = 'doctor'
                        author_profile_id = doc.id
                        author_route = f"/doctor-profile/{doc.id}"
                        author_name = f"Dr. {doc.first_name} {doc.last_name}".strip()
                        author_avatar = doc.profile_dp.url if doc.profile_dp else None
                elif author_role == 'ambulance' or getattr(author_user, 'ambulance', None):
                    amb = getattr(author_user, 'ambulance', None)
                    if amb:
                        author_role = 'ambulance'
                        author_profile_id = amb.id
                        author_route = f"/ambulance-profile/{amb.id}"
                        author_name = amb.owner_name or author_name
                        author_avatar = amb.profile_dp.url if amb.profile_dp else None
                elif author_role == 'pharmacy' or getattr(author_user, 'pharmacy', None):
                    ph = getattr(author_user, 'pharmacy', None)
                    if ph:
                        author_role = 'pharmacy'
                        author_profile_id = ph.id
                        author_route = f"/pharmacy-profile/{ph.id}"
                        author_name = ph.pharmacy_name or author_name
                        author_avatar = ph.profile_dp.url if ph.profile_dp else None
                elif author_role == 'diagnostic' or getattr(author_user, 'diagnostic', None):
                    dg = getattr(author_user, 'diagnostic', None)
                    if dg:
                        author_role = 'diagnostic'
                        author_profile_id = dg.id
                        author_route = f"/diagnostic-profile/{dg.id}"
                        author_name = dg.diagnostic_name or author_name
                        author_avatar = dg.profile_dp.url if dg.profile_dp else None
                elif hasattr(author_user, 'profile') and author_user.profile:
                    prof = author_user.profile
                    author_name = f"{prof.first_name} {prof.last_name}".strip() or author_name
                    author_avatar = prof.profile_dp.url if prof.profile_dp else None
            except Exception:
                pass

        details_data = serializer_class(post).data
        item = {
            "id": post.id,
            "user_email": email,
            "user_id": user_id,
            "author_name": author_name,
            "author_avatar": author_avatar,
            "author_role": author_role,
            "author_profile_id": author_profile_id,
            "author_route": author_route,
            "post_type": post_type,
            "created": post.created,
            "urgency": getattr(post, 'urgency', 'medium'),
            "status": getattr(post, 'status', 'open'),
            "division_name": post.division.division_name_eng if post.division else None,
            "district_name": post.district.district_name_eng if post.district else None,
            "upozila_name": post.upozila.upozila_name_eng if post.upozila else None,
            "likes_count": likes.count(),
            "comments_count": comments_count,
            "shares_count": shares_count,
            "user_has_liked": user_has_liked,
            "details": details_data,
        }
        return Response(APIResponse.success("Post loaded successfully", "post", item))


from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType

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
    """Send in-app + push notification to all followers of author when they create a post."""
    try:
        from interactions.models.user_follow import UserFollow
        from notification.servcies import AppNotificationService, PushNotification
        followers = UserFollow.objects.filter(following=author).select_related('follower')
        author_name = author.email.split('@')[0]
        try:
            if hasattr(author, 'doctor') and author.doctor:
                d = author.doctor
                author_name = f"Dr. {d.first_name} {d.last_name}".strip() or author_name
            elif hasattr(author, 'profile') and author.profile:
                p = author.profile
                author_name = f"{p.first_name} {p.last_name}".strip() or author_name
            elif hasattr(author, 'blood_donor') and author.blood_donor:
                d = author.blood_donor
                author_name = f"{d.first_name} {d.last_name}".strip() or author_name
        except Exception:
            pass
        title = f"{author_name} posted something new"
        message = f"{author_name}: {summary}"
        for follow in followers:
            AppNotificationService.create_notification(
                user=follow.follower,
                title=title,
                message=message,
                post_id=post_id,
                post_type=post_type,
            )
            PushNotification.send_to_user(follow.follower, title, message)
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
        posts = BloodNeedPost.objects.filter(
            is_urgent_post=True,
            status='open'
        ).select_related('user', 'division', 'district', 'upozila').order_by('-created')
        ct = ContentType.objects.get_for_model(BloodNeedPost)
        data = []
        for post in posts:
            likes = PostLike.objects.filter(content_type=ct, object_id=post.id).count()
            comments = PostComment.objects.filter(content_type=ct, object_id=post.id).count()
            user_liked = False
            if request.user.is_authenticated:
                user_liked = PostLike.objects.filter(content_type=ct, object_id=post.id, user=request.user).exists()
            item = BloodNeedPostSerializer(post).data
            item['likes_count'] = likes
            item['comments_count'] = comments
            item['user_has_liked'] = user_liked
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
        return Response(APIResponse.success("Share logged successfully", "share", {"total_shares": total_shares}))


class PostFeedViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        user = request.user
        search = request.query_params.get('search', '').strip().lower()
        post_type_filter = request.query_params.get('post_type', 'all')
        sort_by = request.query_params.get('sort', 'newest')  # newest | oldest | most_liked | most_commented | urgent

        # 1. Fetch all posts
        blood_needs = BloodNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        med_needs = MedicineNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        eq_needs = EquipmentNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        eq_sells = EquipmentSellPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        med_posts = MedicinePost.objects.select_related('user', 'division', 'district', 'upozila').all()
        generals = GeneralPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        amb_needs = AmbulanceNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        donations = BloodDonationPost.objects.select_related('donor__user', 'division', 'district', 'upozila').all()

        feed_items = []

        def add_items(queryset, post_type, serializer_class):
            if post_type_filter != 'all' and post_type_filter != post_type:
                return
            ct = ContentType.objects.get_for_model(queryset.model)
            for post in queryset:
                likes = PostLike.objects.filter(content_type=ct, object_id=post.id)
                comments_count = PostComment.objects.filter(content_type=ct, object_id=post.id).count()
                shares_count = PostShare.objects.filter(content_type=ct, object_id=post.id).count()

                user_has_liked = False
                if user.is_authenticated:
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
                if author_user:
                    try:
                        if hasattr(author_user, 'profile') and author_user.profile:
                            prof = author_user.profile
                            author_name = f"{prof.first_name} {prof.last_name}".strip() or author_name
                            author_avatar = prof.profile_dp.url if prof.profile_dp else None
                        elif hasattr(author_user, 'doctor') and author_user.doctor:
                            doc = author_user.doctor
                            author_name = f"Dr. {doc.first_name} {doc.last_name}".strip()
                            author_avatar = doc.profile_dp.url if doc.profile_dp else None
                        elif hasattr(author_user, 'blood_donor') and author_user.blood_donor:
                            donor = author_user.blood_donor
                            author_name = f"{donor.first_name} {donor.last_name}".strip() or author_name
                            author_avatar = donor.profile_dp.url if donor.profile_dp else None
                        elif hasattr(author_user, 'ambulance') and author_user.ambulance:
                            amb = author_user.ambulance
                            author_name = amb.owner_name or author_name
                            author_avatar = amb.profile_dp.url if amb.profile_dp else None
                        elif hasattr(author_user, 'pharmacy') and author_user.pharmacy:
                            ph = author_user.pharmacy
                            author_name = ph.pharmacy_name or author_name
                            author_avatar = ph.profile_dp.url if ph.profile_dp else None
                        elif hasattr(author_user, 'diagnostic') and author_user.diagnostic:
                            dg = author_user.diagnostic
                            author_name = dg.diagnostic_name or author_name
                            author_avatar = dg.profile_dp.url if dg.profile_dp else None
                    except Exception:
                        pass

                details_data = serializer_class(post).data
                likes_count = likes.count()

                # Server-side search filter
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

                feed_items.append({
                    "id": post.id,
                    "user_email": email,
                    "user_id": user_id,
                    "author_name": author_name,
                    "author_avatar": author_avatar,
                    "post_type": post_type,
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
                })

        add_items(blood_needs, 'blood_need', BloodNeedPostSerializer)
        add_items(med_needs, 'medicine_need', MedicineNeedPostSerializer)
        add_items(eq_needs, 'equipment_need', EquipmentNeedPostSerializer)
        add_items(eq_sells, 'equipment_sell', EquipmentSellPostSerializer)
        add_items(med_posts, 'medicine', MedicinePostSerializer)
        add_items(generals, 'general', GeneralPostSerializer)
        add_items(amb_needs, 'ambulance_need', AmbulanceNeedPostSerializer)
        add_items(donations, 'blood_donation', BloodDonationPostSerializer)

        URGENCY_ORDER = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}

        if sort_by == 'oldest':
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
        else:  # newest (default)
            feed_items.sort(key=lambda x: -x['created'].timestamp() if hasattr(x['created'], 'timestamp') else 0)

        return Response(APIResponse.success("Feed loaded successfully", "feed", feed_items))

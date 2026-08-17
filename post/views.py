from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType

from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination
from core.permissions import IsOwnerOrReadOnly
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.general_post_mod import GeneralPost
from post.models.ambulance_need_mod import AmbulanceNeedPost
from post.models.post_interactions_mod import PostLike, PostComment, PostShare
from profiles.models import BloodDonationPost

from post.serializers import (
    BloodNeedPostSerializer,
    MedicineNeedPostSerializer,
    EquipmentNeedPostSerializer,
    GeneralPostSerializer,
    AmbulanceNeedPostSerializer,
    PostLikeSerializer,
    PostCommentSerializer,
    PostShareSerializer,
)
from donor.serializers import BloodDonationPostSerializer


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
        serializer.save(user=self.request.user)

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
        serializer.save(user=self.request.user)

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
        serializer.save(user=self.request.user)

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
        serializer.save(user=self.request.user)

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
        serializer.save(user=self.request.user)

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


class PostInteractionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_post_model_and_content_type(self, post_type, post_id):
        mapping = {
            'blood_need': (BloodNeedPost, 'bloodneedpost'),
            'medicine_need': (MedicineNeedPost, 'medicineneedpost'),
            'equipment_need': (EquipmentNeedPost, 'equipmentneedpost'),
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
        
        # 1. Fetch all posts
        blood_needs = BloodNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        med_needs = MedicineNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        eq_needs = EquipmentNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        generals = GeneralPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        amb_needs = AmbulanceNeedPost.objects.select_related('user', 'division', 'district', 'upozila').all()
        donations = BloodDonationPost.objects.select_related('donor__user', 'division', 'district', 'upozila').all()
        
        feed_items = []
        
        # Helper to format items
        def add_items(queryset, post_type, serializer_class):
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
                if post_type == 'blood_donation':
                    if post.donor and post.donor.user:
                        email = post.donor.user.email
                        user_id = post.donor.user.id
                else:
                    if post.user:
                        email = post.user.email
                        user_id = post.user.id

                feed_items.append({
                    "id": post.id,
                    "user_email": email,
                    "user_id": user_id,
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
                    "details": serializer_class(post).data
                })

        add_items(blood_needs, 'blood_need', BloodNeedPostSerializer)
        add_items(med_needs, 'medicine_need', MedicineNeedPostSerializer)
        add_items(eq_needs, 'equipment_need', EquipmentNeedPostSerializer)
        add_items(generals, 'general', GeneralPostSerializer)
        add_items(amb_needs, 'ambulance_need', AmbulanceNeedPostSerializer)
        add_items(donations, 'blood_donation', BloodDonationPostSerializer)
        
        # Sort by created desc
        feed_items.sort(key=lambda x: x['created'], reverse=True)
        
        return Response(APIResponse.success("Feed loaded successfully", "feed", feed_items))

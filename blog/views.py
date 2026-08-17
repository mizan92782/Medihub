from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.text import slugify

from core.api_response import APIResponse
from core.pagination import StandardResultsSetPagination
from core.permissions import IsDoctorUser, IsOwnerOrReadOnly
from blog.models import BlogPost, BlogMedia, BlogLike, BlogComment, BlogCommentLike
from blog.serializers import (
    BlogPostSerializer,
    BlogPostCreateUpdateSerializer,
    BlogCommentSerializer,
    BlogMediaSerializer,
)
from profiles.models import Doctor


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Doctor Health Blog Posts.
    - Only doctors can create/update draft or published posts.
    - Public/authenticated users can view published blog posts.
    """
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'doctor']
    search_fields = ['title', 'content', 'tags']
    ordering_fields = ['created', 'views', 'like_count', 'comment_count']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BlogPostCreateUpdateSerializer
        return BlogPostSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsDoctorUser()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.user_type == 'doctor' and hasattr(user, 'doctor'):
            return BlogPost.objects.filter(doctor=user.doctor)
        return BlogPost.objects.filter(status='published').select_related('doctor', 'doctor__user').prefetch_related('media', 'comments').all()

    def perform_create(self, serializer):
        doctor = Doctor.objects.filter(user=self.request.user).first()
        title = serializer.validated_data.get('title')
        slug = slugify(title)
        counter = 1
        original_slug = slug
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        serializer.save(doctor=doctor, slug=slug)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment views
        BlogPost.objects.filter(pk=instance.pk).update(views=instance.views + 1)
        instance.views += 1
        serializer = self.get_serializer(instance)
        return Response(APIResponse.success("Blog post retrieved", "post", serializer.data))

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='like')
    def toggle_like(self, request, pk=None):
        post = self.get_object()
        liked = BlogLike.remove_like(post=post, user=request.user)
        if not liked:
            BlogLike.add_like(post=post, user=request.user)
            return Response(APIResponse.success("Blog post liked", "liked", True))
        return Response(APIResponse.success("Blog post unliked", "liked", False))


class BlogCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Blog Comments & Nested Replies.
    """
    serializer_class = BlogCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'parent']

    def get_queryset(self):
        return BlogComment.objects.filter(parent=None).select_related('user', 'post').prefetch_related('replies').all()

    def create(self, request, *args, **kwargs):
        post_id = request.data.get('post')
        content = request.data.get('content')
        parent_id = request.data.get('parent')
        if not post_id or not content:
            return Response(APIResponse.error("post and content are required"), status=status.HTTP_400_BAD_REQUEST)
        
        post = BlogPost.objects.filter(pk=post_id).first()
        if not post:
            return Response(APIResponse.error("Blog post not found"), status=status.HTTP_404_NOT_FOUND)

        parent = None
        if parent_id:
            parent = BlogComment.objects.filter(pk=parent_id).first()

        comment = BlogComment.add_comment(post=post, user=request.user, content=content, parent=parent)
        serializer = self.get_serializer(comment)
        return Response(APIResponse.success("Comment added successfully", "comment", serializer.data), status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        comment_id = kwargs.get('pk')
        success = BlogComment.remove_comment(comment_id=comment_id, user=request.user)
        if success:
            return Response(APIResponse.success("Comment deleted successfully"))
        return Response(APIResponse.error("Failed to delete comment or unauthorized"), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='like')
    def toggle_like(self, request, pk=None):
        comment = self.get_object()
        removed = BlogCommentLike.remove_like(comment=comment, user=request.user)
        if not removed:
            BlogCommentLike.add_like(comment=comment, user=request.user)
            return Response(APIResponse.success("Comment liked", "liked", True))
        return Response(APIResponse.success("Comment unliked", "liked", False))

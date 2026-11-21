from django.urls import path
from rest_framework.routers import DefaultRouter
from blog.views import BlogPostViewSet, BlogCommentViewSet, upload_blog_image

router = DefaultRouter()
router.register('posts', BlogPostViewSet, basename='blog-post')
router.register('comments', BlogCommentViewSet, basename='blog-comment')

urlpatterns = router.urls + [
    path('upload-image/', upload_blog_image, name='blog-upload-image'),
]

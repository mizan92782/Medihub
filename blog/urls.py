from rest_framework.routers import DefaultRouter
from blog.views import BlogPostViewSet, BlogCommentViewSet

router = DefaultRouter()
router.register('posts', BlogPostViewSet, basename='blog-post')
router.register('comments', BlogCommentViewSet, basename='blog-comment')

urlpatterns = router.urls

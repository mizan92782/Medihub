from rest_framework.routers import DefaultRouter
from interactions.views import DoctorFollowViewSet, DoctorQAViewSet, DoctorProfileTrackerView, UserFollowViewSet

router = DefaultRouter()
router.register('follow', DoctorFollowViewSet, basename='doctor-follow')
router.register('qa', DoctorQAViewSet, basename='doctor-qa')
router.register('tracker', DoctorProfileTrackerView, basename='doctor-tracker')
router.register('user-follow', UserFollowViewSet, basename='user-follow')

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter
from interactions.views import DoctorFollowViewSet, DoctorQAViewSet, DoctorProfileTrackerView

router = DefaultRouter()
router.register('follow', DoctorFollowViewSet, basename='doctor-follow')
router.register('qa', DoctorQAViewSet, basename='doctor-qa')
router.register('tracker', DoctorProfileTrackerView, basename='doctor-tracker')

urlpatterns = router.urls

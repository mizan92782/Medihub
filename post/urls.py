from rest_framework.routers import DefaultRouter
from post.views import (
    BloodNeedPostViewSet,
    MedicineNeedPostViewSet,
    EquipmentNeedPostViewSet,
    GeneralPostViewSet,
    AmbulanceNeedPostViewSet,
    PostInteractionViewSet,
    PostFeedViewSet,
)

router = DefaultRouter()
router.register('blood-need', BloodNeedPostViewSet, basename='blood-need-post')
router.register('medicine-need', MedicineNeedPostViewSet, basename='medicine-need-post')
router.register('equipment-need', EquipmentNeedPostViewSet, basename='equipment-need-post')
router.register('general', GeneralPostViewSet, basename='general-post')
router.register('ambulance-need', AmbulanceNeedPostViewSet, basename='ambulance-need-post')
router.register('interactions', PostInteractionViewSet, basename='post-interaction')
router.register('feed', PostFeedViewSet, basename='post-feed')

urlpatterns = router.urls

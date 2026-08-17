from rest_framework.routers import DefaultRouter
from location.views import DivisionViewSet, DistrictViewSet, UpozilaViewSet, UnionViewSet

router = DefaultRouter()
router.register('divisions', DivisionViewSet, basename='division')
router.register('districts', DistrictViewSet, basename='district')
router.register('upazilas', UpozilaViewSet, basename='upozila')
router.register('unions', UnionViewSet, basename='union')

urlpatterns = router.urls

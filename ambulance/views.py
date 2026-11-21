from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsOwnerOrReadOnly
from core.pagination import StandardResultsSetPagination
from profiles.models import AmbulanceProfile, AmbulanceReview
from .serializers import AmbulanceProfileSerializer, AmbulanceReviewSerializer
from .tasks import notify_ambulance_owner_on_review


class AmbulanceViewSet(viewsets.ModelViewSet):
    queryset = AmbulanceProfile.objects.filter(is_active=True)
    serializer_class = AmbulanceProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['ambulance_type']
    search_fields = ['owner_name', 'vehicle_number', 'contact_number', 'address']

    @action(detail=True, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        ambulance = self.get_object()
        if request.method == 'GET':
            reviews = AmbulanceReview.objects.filter(ambulance=ambulance)
            serializer = AmbulanceReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        if AmbulanceReview.objects.filter(ambulance=ambulance, user=request.user).exists():
            raise ValidationError('You have already reviewed this ambulance.')
        serializer = AmbulanceReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(user=request.user, ambulance=ambulance)
        notify_ambulance_owner_on_review.delay(
            ambulance_id=ambulance.pk,
            reviewer_email=request.user.email,
            rating=review.rating,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'reviews/(?P<review_pk>\d+)',
            permission_classes=[permissions.IsAuthenticated])
    def delete_review(self, request, pk=None, review_pk=None):
        review = AmbulanceReview.objects.filter(pk=review_pk, ambulance_id=pk, user=request.user).first()
        if not review:
            return Response({'detail': 'Not found or not your review.'}, status=status.HTTP_404_NOT_FOUND)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from rest_framework import serializers
from profiles.models import AmbulanceProfile, AmbulanceReview


class AmbulanceProfileSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = AmbulanceProfile
        fields = '__all__'

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews.exists():
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    def get_total_reviews(self, obj):
        return obj.reviews.count()


class AmbulanceReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AmbulanceReview
        fields = ['id', 'ambulance', 'user', 'user_email', 'rating', 'opinion', 'created']
        read_only_fields = ['user', 'ambulance', 'created']

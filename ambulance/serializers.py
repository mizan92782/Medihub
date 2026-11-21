from rest_framework import serializers
from profiles.models import AmbulanceProfile, AmbulanceReview
from interactions.models.user_follow import UserFollow


class AmbulanceProfileSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

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

    def get_followers_count(self, obj):
        return UserFollow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj):
        return UserFollow.objects.filter(follower=obj.user).count()


class AmbulanceReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AmbulanceReview
        fields = ['id', 'ambulance', 'user', 'user_email', 'rating', 'opinion', 'created']
        read_only_fields = ['user', 'ambulance', 'created']

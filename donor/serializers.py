from rest_framework import serializers
from profiles.models import BloodDonor, BloodDonationPost
from interactions.models.user_follow import UserFollow

class BloodDonorSerializer(serializers.ModelSerializer):
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = BloodDonor
        fields = '__all__'

    def get_followers_count(self, obj):
        return UserFollow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj):
        return UserFollow.objects.filter(follower=obj.user).count()

class BloodDonationPostSerializer(serializers.ModelSerializer):
    donor_detail = BloodDonorSerializer(source='donor', read_only=True)

    class Meta:
        model = BloodDonationPost
        fields = '__all__'
        ref_name = 'DonorBloodDonationPost'

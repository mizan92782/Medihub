from rest_framework import serializers
from profiles.models import BloodDonor, BloodDonationPost
from interactions.models.user_follow import UserFollow

class BloodDonationHistorySerializer(serializers.ModelSerializer):
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = BloodDonationPost
        fields = [
            'id', 'patient_description', 'medical_facility',
            'donation_date', 'donation_time', 'bags_donated',
            'division', 'district', 'upozila',
            'division_name', 'district_name', 'upozila_name',
            'created'
        ]

class BloodDonorSerializer(serializers.ModelSerializer):
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_email = serializers.ReadOnlyField(source='user.email')
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    donation_posts = BloodDonationHistorySerializer(many=True, read_only=True)

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


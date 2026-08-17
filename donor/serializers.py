from rest_framework import serializers
from profiles.models import BloodDonor, BloodDonationPost

class BloodDonorSerializer(serializers.ModelSerializer):
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = BloodDonor
        fields = '__all__'

class BloodDonationPostSerializer(serializers.ModelSerializer):
    donor_detail = BloodDonorSerializer(source='donor', read_only=True)

    class Meta:
        model = BloodDonationPost
        fields = '__all__'

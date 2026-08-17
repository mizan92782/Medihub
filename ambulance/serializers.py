from rest_framework import serializers
from profiles.models import AmbulanceProfile

class AmbulanceProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AmbulanceProfile
        fields = '__all__'

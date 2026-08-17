from rest_framework import serializers
from profiles.models import DiagnosticProfile, DiagnosticTest

class DiagnosticProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticProfile
        fields = '__all__'

class DiagnosticTestSerializer(serializers.ModelSerializer):
    diagnostic_name = serializers.ReadOnlyField(source='diagnostic.diagnostic_name')
    contact_number = serializers.ReadOnlyField(source='diagnostic.contact_number')

    class Meta:
        model = DiagnosticTest
        fields = '__all__'

from rest_framework import serializers
from profiles.models import PharmacyProfile, PharmacyMedicine

class PharmacyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyProfile
        fields = '__all__'

class PharmacyMedicineSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.pharmacy_name')
    contact_number = serializers.ReadOnlyField(source='pharmacy.contact_number')

    class Meta:
        model = PharmacyMedicine
        fields = '__all__'

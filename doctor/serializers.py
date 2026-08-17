from rest_framework import serializers
from profiles.models import (
    Doctor, Specialization, SubSpecialization, Qualification,
    Hospital, DoctorBooking, DoctorRating, DoctorStats, DoctorDetails
)

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'

class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'

class DoctorStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorStats
        fields = '__all__'

class DoctorSerializer(serializers.ModelSerializer):
    specialization_detail = SpecializationSerializer(source='specialization', read_only=True)
    qualifications_detail = QualificationSerializer(source='qualifications', many=True, read_only=True)
    hospitals_detail = HospitalSerializer(source='hospital_affiliations', many=True, read_only=True)
    evaluation = DoctorStatsSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')

    class Meta:
        model = Doctor
        fields = '__all__'

class DoctorBookingSerializer(serializers.ModelSerializer):
    doctor_detail = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = DoctorBooking
        fields = '__all__'

class DoctorRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorRating
        fields = '__all__'

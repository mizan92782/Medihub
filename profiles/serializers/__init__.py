from rest_framework import serializers
from authentication.serializer import UserSerializer
from location.models import Division, District, Upozila, Union
from profiles.models import (
    RegularUserProfile,
    Doctor,
    DoctorDetails,
    DoctorEducation,
    DoctorWorkingExperience,
    DoctorScheduling,
    DoctorDateSlot,
    DoctorRating,
    DoctorBooking,
    DoctorStats,
    Specialization,
    SubSpecialization,
    Qualification,
    Hospital,
    BloodDonor,
    BloodDonationPost,
    AmbulanceProfile,
    PharmacyProfile,
    PharmacyMedicine,
    DiagnosticProfile,
    DiagnosticTest,
)


# Location helper serializers
class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = ['id', 'division_id', 'division_name_eng', 'division_name_bn']


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'district_id', 'district_name_eng', 'district_name_bn', 'lattitude', 'logitude']


class UpozilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upozila
        fields = ['id', 'upozila', 'upozila_name_eng', 'upoila_name_bn']


class UnionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Union
        fields = ['id', 'union', 'union_name_eng', 'union_name_bn']


# Medical metadata serializers
class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = '__all__'


class SubSpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSpecialization
        fields = '__all__'


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'


# Regular User Profile
class RegularUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = RegularUserProfile
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


# Doctor Sub-models Serializers
class DoctorDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDetails
        fields = '__all__'
        read_only_fields = ['doctor']


class DoctorEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorEducation
        fields = '__all__'
        read_only_fields = ['doctor']


class DoctorWorkingExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorWorkingExperience
        fields = '__all__'
        read_only_fields = ['doctor']


class DoctorSchedulingSerializer(serializers.ModelSerializer):
    hospital_name = serializers.ReadOnlyField(source='hospital.name_eng')

    class Meta:
        model = DoctorScheduling
        fields = '__all__'
        read_only_fields = ['doctor']


class DoctorDateSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='schedule.doctor.__str__')
    start_time = serializers.ReadOnlyField(source='schedule.start')
    end_time = serializers.ReadOnlyField(source='schedule.end')
    hospital_name = serializers.ReadOnlyField(source='schedule.hospital.name_eng')

    class Meta:
        model = DoctorDateSlot
        fields = '__all__'


class DoctorStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorStats
        fields = '__all__'


class DoctorRatingSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorRating
        fields = ['id', 'doctor', 'user', 'user_name', 'rating', 'review', 'created']
        read_only_fields = ['user', 'created']

    def get_user_name(self, obj):
        return f"{obj.user.email}"


class DoctorBookingSerializer(serializers.ModelSerializer):
    doctor_name = serializers.ReadOnlyField(source='doctor.__str__')
    user_email = serializers.ReadOnlyField(source='user.email')
    date_slot_detail = DoctorDateSlotSerializer(source='date_slot', read_only=True)

    class Meta:
        model = DoctorBooking
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


# Main Doctor Profile Serializer
class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specialization_detail = SpecializationSerializer(source='specialization', read_only=True)
    sub_specialization_detail = SubSpecializationSerializer(source='sub_specialization', read_only=True)
    qualifications_detail = QualificationSerializer(source='qualifications', many=True, read_only=True)
    hospitals_detail = HospitalSerializer(source='hospital_affiliations', many=True, read_only=True)
    details = DoctorDetailsSerializer(read_only=True)
    educations = DoctorEducationSerializer(many=True, read_only=True)
    experiences = DoctorWorkingExperienceSerializer(many=True, read_only=True)
    schedules = DoctorSchedulingSerializer(many=True, read_only=True)
    evaluation = DoctorStatsSerializer(read_only=True)

    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    union_name = serializers.ReadOnlyField(source='union.union_name_eng')

    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ['user', 'license_number', 'created', 'updated']


# Blood Donor Serializers
class BloodDonationPostSerializer(serializers.ModelSerializer):
    donor_name = serializers.ReadOnlyField(source='donor.__str__')

    class Meta:
        model = BloodDonationPost
        fields = '__all__'
        read_only_fields = ['donor', 'created']


class BloodDonorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    donation_posts = BloodDonationPostSerializer(many=True, read_only=True)

    class Meta:
        model = BloodDonor
        fields = '__all__'
        read_only_fields = ['user', 'lives_saved_count', 'created', 'updated']


# Ambulance Profile Serializer
class AmbulanceProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = AmbulanceProfile
        fields = '__all__'
        read_only_fields = ['user', 'vehicle_number', 'created', 'updated']


# Pharmacy Serializers
class PharmacyMedicineSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.ReadOnlyField(source='pharmacy.pharmacy_name')
    contact_number = serializers.ReadOnlyField(source='pharmacy.contact_number')

    class Meta:
        model = PharmacyMedicine
        fields = '__all__'
        read_only_fields = ['pharmacy', 'created', 'updated']


class PharmacyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = PharmacyProfile
        fields = '__all__'
        read_only_fields = ['user', 'license_number', 'created', 'updated']


# Diagnostic Serializers
class DiagnosticTestSerializer(serializers.ModelSerializer):
    diagnostic_name = serializers.ReadOnlyField(source='diagnostic.diagnostic_name')
    contact_number = serializers.ReadOnlyField(source='diagnostic.contact_number')

    class Meta:
        model = DiagnosticTest
        fields = '__all__'
        read_only_fields = ['diagnostic', 'created', 'updated']


class DiagnosticProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = DiagnosticProfile
        fields = '__all__'
        read_only_fields = ['user', 'license_number', 'created', 'updated']

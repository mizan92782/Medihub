from rest_framework import serializers
from interactions.models.user_docotor_interaction import (
    UserDoctorInteractionFollwDoctor,
    UserDoctorInteractionAskQuestion,
    UserDoctorInteractionProfileShow,
)
from profiles.serializers import DoctorProfileSerializer


class DoctorFollowSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    doctor_name = serializers.ReadOnlyField(source='doctor.__str__')

    class Meta:
        model = UserDoctorInteractionFollwDoctor
        fields = ['id', 'user', 'user_email', 'doctor', 'doctor_name', 'follow', 'created_at']
        read_only_fields = ['user', 'created_at']


class DoctorAskQuestionSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    doctor_name = serializers.ReadOnlyField(source='doctor.__str__')

    class Meta:
        model = UserDoctorInteractionAskQuestion
        fields = ['id', 'user', 'user_email', 'doctor', 'doctor_name', 'question', 'created_at']
        read_only_fields = ['user', 'created_at']


class DoctorProfileShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDoctorInteractionProfileShow
        fields = ['id', 'user', 'doctor', 'created_at']
        read_only_fields = ['user', 'created_at']

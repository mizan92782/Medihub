from rest_framework import serializers
from authentication.serializer import UserSerializer
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.general_post_mod import GeneralPost


class BloodNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = BloodNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class MedicineNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = MedicineNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class EquipmentNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = EquipmentNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class GeneralPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = GeneralPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


from post.models.ambulance_need_mod import AmbulanceNeedPost
from post.models.post_interactions_mod import PostLike, PostComment, PostShare

class AmbulanceNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')

    class Meta:
        model = AmbulanceNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class PostLikeSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = PostLike
        fields = '__all__'
        read_only_fields = ['user']


class PostCommentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = PostComment
        fields = '__all__'
        read_only_fields = ['user']


class PostShareSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = PostShare
        fields = '__all__'
        read_only_fields = ['user']


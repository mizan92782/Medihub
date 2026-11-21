from rest_framework import serializers
from authentication.serializer import UserSerializer
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.equipment_sell_mod import EquipmentSellPost
from post.models.medicine_post_mod import MedicinePost
from post.models.general_post_mod import GeneralPost
from post.models.post_image_mod import PostImage
from django.contrib.contenttypes.models import ContentType


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'order']


def get_post_images(post_instance):
    ct = ContentType.objects.get_for_model(post_instance.__class__)
    images = PostImage.objects.filter(content_type=ct, object_id=post_instance.id)
    return PostImageSerializer(images, many=True).data


class BloodNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

    class Meta:
        model = BloodNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class MedicineNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

    class Meta:
        model = MedicineNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class EquipmentNeedPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

    class Meta:
        model = EquipmentNeedPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class EquipmentSellPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

    class Meta:
        model = EquipmentSellPost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class MedicinePostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

    class Meta:
        model = MedicinePost
        fields = '__all__'
        read_only_fields = ['user', 'created', 'updated']


class GeneralPostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    division_name = serializers.ReadOnlyField(source='division.division_name_eng')
    district_name = serializers.ReadOnlyField(source='district.district_name_eng')
    upozila_name = serializers.ReadOnlyField(source='upozila.upozila_name_eng')
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

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
    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return get_post_images(obj)

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


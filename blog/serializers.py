from rest_framework import serializers
from authentication.serializer import UserSerializer
from blog.models import BlogPost, BlogMedia, BlogLike, BlogComment, BlogCommentLike
from profiles.serializers import DoctorProfileSerializer


class BlogMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogMedia
        fields = '__all__'


class BlogCommentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    user_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'user', 'user_email', 'user_name', 'parent', 'content', 'like_count', 'replies', 'created', 'updated']
        read_only_fields = ['user', 'like_count', 'created', 'updated']

    def get_user_name(self, obj):
        if not obj.user:
            return "User"
        u = obj.user
        if hasattr(u, 'doctor') and u.doctor:
            doc_name = f"Dr. {u.doctor.first_name} {u.doctor.last_name}".strip()
            if doc_name != "Dr.":
                return doc_name
        if hasattr(u, 'regularuserprofile') and u.regularuserprofile and getattr(u.regularuserprofile, 'name', None):
            return u.regularuserprofile.name
        if hasattr(u, 'blood_donor_profile') and u.blood_donor_profile:
            donor_name = f"{u.blood_donor_profile.first_name} {u.blood_donor_profile.last_name}".strip()
            if donor_name:
                return donor_name
        return u.email.split('@')[0] if u.email else "User"

    def get_replies(self, obj):
        if obj.replies.exists():
            return BlogCommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []


class BlogPostSerializer(serializers.ModelSerializer):
    doctor_detail = DoctorProfileSerializer(source='doctor', read_only=True)
    media = BlogMediaSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = '__all__'
        read_only_fields = ['doctor', 'slug', 'views', 'like_count', 'comment_count', 'created', 'updated']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return BlogLike.objects.filter(post=obj, user=request.user).exists()
        return False


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category', 'tags', 'thumbnail', 'status']

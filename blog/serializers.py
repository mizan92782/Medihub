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
    replies = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = ['id', 'post', 'user', 'user_email', 'parent', 'content', 'like_count', 'replies', 'created', 'updated']
        read_only_fields = ['user', 'like_count', 'created', 'updated']

    def get_replies(self, obj):
        if obj.replies.exists():
            return BlogCommentSerializer(obj.replies.all(), many=True).data
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

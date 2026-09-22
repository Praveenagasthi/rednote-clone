from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.models import Post
from posts.serializers import PostImageSerializer

User = get_user_model()


class SearchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'display_name',
            'avatar',
        ]


class SearchPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    images = PostImageSerializer(many=True, read_only=True)

    likes_count = serializers.IntegerField(
        source='likes.count',
        read_only=True
    )

    saves_count = serializers.IntegerField(
        source='saves.count',
        read_only=True
    )

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'caption',
            'location',
            'images',
            'likes_count',
            'saves_count',
            'created_at',
        ]
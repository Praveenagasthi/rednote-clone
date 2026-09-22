from rest_framework import serializers
from .models import Post, PostImage, Like, Comment, Save


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'order']

    def validate_image(self, image):
        max_size = 10 * 1024 * 1024  # 10 MB

        if image.size > max_size:
            raise serializers.ValidationError(
                "Image size cannot exceed 10 MB."
            )

        return image

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'user_id',
            'text',
            'created_at',
            'updated_at'
        ]

    def validate_text(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Comment cannot be empty."
            )

        if len(value) > 1000:
            raise serializers.ValidationError(
                "Comment cannot exceed 1000 characters."
            )

        return value

class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    author_id = serializers.IntegerField(source='author.id',read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    hashtags = serializers.SerializerMethodField()

    likes_count = serializers.IntegerField(
        source='likes.count',
        read_only=True
    )

    saves_count = serializers.IntegerField(
        source='saves.count',
        read_only=True
    )

    comment_count = serializers.IntegerField(
        source='comments.count',
        read_only=True
    )

    liked_by_me = serializers.SerializerMethodField()
    saved_by_me = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'author',
            'author_id',
            'caption',
            'location',
            'images',
            'comments',
            'comment_count',
            'hashtags',
            'likes_count',
            'saves_count',
            'liked_by_me',
            'saved_by_me',
            'is_owner',
            'created_at',
            'updated_at',
        ]

    def validate_caption(self, value):
        value = value.strip()

        if len(value) > 2000:
            raise serializers.ValidationError(
                "Caption cannot exceed 2000 characters."
            )

        return value

    def validate_location(self, value):
        value = value.strip()

        if len(value) > 255:
            raise serializers.ValidationError(
                "Location cannot exceed 255 characters."
            )

        return value

    def get_liked_by_me(self, obj):
        return getattr(obj, 'liked_by_me_query', False)

    def get_saved_by_me(self, obj):
        return getattr(obj, 'saved_by_me_query', False)

    def get_is_owner(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False

        return obj.author == request.user

    def get_hashtags(self, obj):
        return [
            hashtag.name
            for hashtag in obj.hashtags.all()
        ]
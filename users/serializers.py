from django.contrib.auth import get_user_model
from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password

from posts.models import Follow, Notification

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(
        source='followers.count',
        read_only=True
    )

    following_count = serializers.IntegerField(
        source='following.count',
        read_only=True
    )

    posts_count = serializers.IntegerField(
        source='posts.count',
        read_only=True
    )

    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'display_name',
            'avatar',
            'bio',
            'followers_count',
            'following_count',
            'posts_count',
            'is_following',
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')

        if not request or not request.user.is_authenticated:
            return False

        if request.user == obj:
            return False

        return obj.followers.filter(
            follower=request.user
        ).exists()

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'display_name',
            'bio',
            'avatar',
        ]

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'display_name',
            'avatar',
        ]

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserListSerializer(read_only=True)
    notification_type = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'sender',
            'notification_type',
            'post',
            'comment',
            'is_read',
            'created_at',
        ]
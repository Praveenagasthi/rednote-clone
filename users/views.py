from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.models import Follow,Post, Notification
from posts.serializers import PostSerializer

from .serializers import (
    RegisterSerializer, 
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserListSerializer,
    NotificationSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class FollowToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            target_user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'detail': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if target_user == request.user:
            return Response(
                {'detail': 'You cannot follow yourself.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow = Follow.objects.filter(
            follower=request.user,
            following=target_user
        ).first()

        if follow:
            follow.delete()
            following = False

        else:
            Follow.objects.create(
                follower=request.user,
                following=target_user
            )

            # Create notification
            Notification.objects.create(
                recipient=target_user,
                sender=request.user,
                notification_type='follow'
            )

            following = True

        return Response({
            'following': following
        })

class UserProfileView(generics.RetrieveAPIView):

    queryset = (
        User.objects
        .prefetch_related(
            'posts',
            'followers',
            'following',
        )
    )

    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Post.objects
            .filter(author_id=self.kwargs['pk'])
            .select_related('author')
            .prefetch_related(
                'images',
                'comments__user',
                'hashtags',
                'likes',
                'saves',
            )
            .order_by('-created_at')
        )


class FollowersView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            User.objects
            .filter(
                following__following_id=self.kwargs['pk']
            )
            .only(
                'id',
                'username',
                'display_name',
                'avatar',
            )
            .order_by('username')
        )


class FollowingView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            User.objects
            .filter(
                followers__follower_id=self.kwargs['pk']
            )
            .only(
                'id',
                'username',
                'display_name',
                'avatar',
            )
            .order_by('username')
        )

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related(
            'sender',
            'post',
            'comment'
        ).order_by('-created_at')

class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(
                pk=pk,
                recipient=request.user
            )
        except Notification.DoesNotExist:
            return Response(
                {'detail': 'Notification not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save(update_fields=['is_read'])

        return Response({
            'id': notification.id,
            'is_read': notification.is_read
        })

class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({
            'unread_count': count
        })

class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            'marked_read': updated_count
        })
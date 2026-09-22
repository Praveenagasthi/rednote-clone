from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from posts.models import Post

from .serializers import (
    SearchUserSerializer,
    SearchPostSerializer,
)

User = get_user_model()


class UserSearchView(generics.ListAPIView):
    serializer_class = SearchUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()

        if not query:
            return User.objects.none()

        return (
            User.objects
            .filter(
                Q(username__icontains=query) |
                Q(display_name__icontains=query)
            )
            .only(
                'id',
                'username',
                'display_name',
                'avatar',
            )
            .order_by('username')
        )

class PostSearchView(generics.ListAPIView):
    serializer_class = SearchPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()

        if not query:
            return Post.objects.none()

        return (
            Post.objects
            .filter(
                Q(caption__icontains=query) |
                Q(location__icontains=query)
            )
            .select_related('author')
            .prefetch_related(
                'images',
                'likes',
                'saves',
            )
            .order_by('-created_at')
        )
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from django.db.models import Exists, OuterRef

from posts.models import Post, Like, Save
from posts.serializers import PostSerializer

User = get_user_model()


class HomeFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = user.following.values_list(
            'following_id',
            flat=True
        )

        return (
            Post.objects
            .filter(
                author_id__in=list(following_ids) + [user.id]
            )
            .select_related('author')
            .annotate(
                liked_by_me_query=Exists(
                    Like.objects.filter(
                        user=user,
                        post=OuterRef('pk')
                    )
                ),
                saved_by_me_query=Exists(
                    Save.objects.filter(
                        user=user,
                        post=OuterRef('pk')
                    )
                ),
            )
            .prefetch_related(
                'images',
                'comments__user',
                'hashtags',
                'likes',
                'saves',
            )
            .order_by('-created_at')
        )


class ExploreFeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_ids = user.following.values_list(
            'following_id',
            flat=True
        )

        return (
            Post.objects
            .exclude(
                author_id__in=list(following_ids) + [user.id]
            )
            .select_related('author')
            .annotate(
                liked_by_me_query=Exists(
                    Like.objects.filter(
                        user=user,
                        post=OuterRef('pk')
                    )
                ),
                saved_by_me_query=Exists(
                    Save.objects.filter(
                        user=user,
                        post=OuterRef('pk')
                    )
                ),
            )
            .prefetch_related(
                'images',
                'comments__user',
                'hashtags',
                'likes',
                'saves',
            )
            .order_by('-created_at')
        )
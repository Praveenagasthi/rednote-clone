import re

from django.db import transaction
from django.db.models import Exists, OuterRef

from django.shortcuts import get_object_or_404

from rest_framework import generics, status, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.parsers import MultiPartParser, FormParser

from .models import( 
    Post, 
    PostImage, 
    Like, 
    Save, 
    Comment, 
    Hashtag, 
    Notification,
)
from .serializers import (
    PostSerializer,
    CommentSerializer,
)

class PostListCreateView(generics.ListCreateAPIView):

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Post.objects
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

        if user.is_authenticated:
            queryset = queryset.annotate(
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

        return queryset
    
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # print("USER:", self.request.user)
        # print("AUTHENTICATED:", self.request.user.is_authenticated)

        with transaction.atomic():
            post = serializer.save(author=self.request.user)

            images = self.request.FILES.getlist('images')

            if len(images) > 10:
                raise serializers.ValidationError(
                    "A post can contain a maximum of 10 images."
                )

            max_size = 10 * 1024 * 1024  # 10 MB

            for index, image in enumerate(images):

                if image.size > max_size:
                    raise serializers.ValidationError(
                        f"Image '{image.name}' exceeds the 10 MB limit."
                    )

                try:
                    from PIL import Image

                    img = Image.open(image)
                    img.verify()

                    image.seek(0)

                except Exception:
                    raise serializers.ValidationError(
                        f"'{image.name}' is not a valid image."
                    )

                PostImage.objects.create(
                    post=post,
                    image=image,
                    order=index
                )

            hashtags = re.findall(
                r'#([A-Za-z0-9_]+)',
                post.caption
            )

            for hashtag_name in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(
                    name=hashtag_name.lower()
                )

                hashtag.posts.add(post)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        user = self.request.user

        queryset = (
            Post.objects
            .select_related('author')
            .prefetch_related(
                'images',
                'comments__user',
                'hashtags',
                'likes',
                'saves',
            )
        )

        if user.is_authenticated:
            queryset = queryset.annotate(
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
                )
            )

        return queryset

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied(
                "You can only edit your own posts."
            )

        post = serializer.save()

        post.hashtags.clear()

        hashtags = re.findall(
            r'#([A-Za-z0-9_]+)',
            post.caption
        )

        for hashtag_name in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(
                name=hashtag_name.lower()
            )

            hashtag.posts.add(post)

        Hashtag.objects.filter(
            posts__isnull=True
        ).delete()

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied(
                "You can only delete your own posts."
            )

        
        instance.delete()

class LikeToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        like = Like.objects.filter(
            user=request.user,
            post=post
        ).first()

        if like:
            like.delete()
            liked = False

        else:
            Like.objects.create(
                user=request.user,
                post=post
            )

            # Create notification
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post
                )

            liked = True

        return Response({
            'liked': liked,
            'likes_count': post.likes.count()
        })

class SaveToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {'detail': 'Post not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        save = Save.objects.filter(
            user=request.user,
            post=post
        ).first()

        if save:
            save.delete()
            saved = False
        else:
            Save.objects.create(
                user=request.user,
                post=post
            )
            saved = True

        return Response({
            'saved': saved,
            'saves_count': post.saves.count()
        })

class SavedPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Post.objects
            .filter(saves__user=self.request.user)
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

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(
            post_id=self.kwargs['pk']
        ).order_by('created_at')

    def perform_create(self, serializer):
        post = get_object_or_404(
            Post,
            pk=self.kwargs['pk']
        )

        comment = serializer.save(
            user=self.request.user,
            post=post
        )

        # Create notification
        if post.author != self.request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=self.request.user,
                notification_type='comment',
                post=post,
                comment=comment
            )

class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You can only delete your own comments."
            )

        instance.delete()

class HashtagPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hashtag_name = self.kwargs['name'].lower()

        return Post.objects.filter(
            hashtags__name=hashtag_name
        ).order_by('-created_at')
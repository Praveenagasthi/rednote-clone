from django.urls import path

from .views import (
    PostListCreateView,
    PostDetailView,
    LikeToggleView,
    SaveToggleView,
    SavedPostsView,
    CommentListCreateView,
    CommentDeleteView,
    HashtagPostsView,
)


urlpatterns = [
    path('', PostListCreateView.as_view(), name='post-list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path(
        '<int:pk>/like/',
        LikeToggleView.as_view(),
        name='post-like'
    ),

    path(
        '<int:pk>/save/',
        SaveToggleView.as_view(),
        name='post-save'
    ),

    path(
        'saved/',
        SavedPostsView.as_view(),
        name='saved-posts'
    ),

    path(
        '<int:pk>/comments/',
        CommentListCreateView.as_view(),
        name='post-comments'
    ),

    path(
        'comments/<int:pk>/delete/',
        CommentDeleteView.as_view(),
        name='comment-delete'
),

    path(
        'hashtags/<str:name>/',
        HashtagPostsView.as_view(),
        name='hashtag-posts'
    ),


]
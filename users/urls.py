from django.urls import path

from .views import (
    RegisterView,
    FollowToggleView,
    UserProfileView,
    UserProfileUpdateView,
    UserPostsView,
    FollowersView,
    FollowingView,
    NotificationListView,
    NotificationReadView,
    NotificationUnreadCountView,
    NotificationMarkAllReadView,

)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path(
        'users/<int:pk>/follow/',
        FollowToggleView.as_view(),
        name='user-follow'
    ),

    path(
        'users/<int:pk>/',
        UserProfileView.as_view(),
        name='user-profile'
    ),

    path(
        'users/me/update/',
        UserProfileUpdateView.as_view(),
        name='user-profile-update'
    ),

    path(
        'users/<int:pk>/posts/',
        UserPostsView.as_view(),
        name='user-posts'
    ),

    path(
        'users/<int:pk>/followers/',
        FollowersView.as_view(),
        name='user-followers'
    ),

    path(
        'users/<int:pk>/following/',
        FollowingView.as_view(),
        name='user-following'
    ),

    path(
        'notifications/',
        NotificationListView.as_view(),
        name='notifications'
    ),

    path(
        'notifications/<int:pk>/read/',
        NotificationReadView.as_view(),
        name='notification-read'
    ),

    path(
        'notifications/unread-count/',
        NotificationUnreadCountView.as_view(),
        name='notification-unread-count'
    ),

    path(
        'notifications/read-all/',
        NotificationMarkAllReadView.as_view(),
        name='notification-read-all'
    ),
]
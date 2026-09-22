from django.urls import path

from .views import HomeFeedView, ExploreFeedView


urlpatterns = [
    path('', HomeFeedView.as_view(), name='home-feed'),
    path('explore/', ExploreFeedView.as_view(), name='explore-feed'),
]
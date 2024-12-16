from django.urls import path
from .views import PostList, RatingView, RegisterView, AnalyticsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('posts/', PostList.as_view(), name='post-list'),
    path('ratings/', RatingView.as_view(), name='rating'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]

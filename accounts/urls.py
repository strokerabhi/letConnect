
from django.contrib import admin
from django.urls import path
from .views import registrationView, loginAPIView, UserProfileView

urlpatterns = [
    path('register/', registrationView.as_view(), name='register'),
    path('login/', loginAPIView.as_view(), name='login'),
    path('my-profile/', UserProfileView.as_view(), name='profile'),
]
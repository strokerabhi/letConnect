
from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('serach/', userSearchAPIViews.as_view(), name='user-search'),
    path('friend-request/send/', SendFriendRequestApiView.as_view(), name='send-friend-request'),
    path('friend-request/accept/', AcceptFriendRequestApiView.as_view(), name='accept-friend-request'),

    path('friend-lists/', FriendListView.as_view(), name='friend-list'),
    path('pending-lists/', PendingFriendRequestsListView.as_view(), name='pending-list'),
]
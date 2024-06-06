from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import *
from accounts.views import registrationView
from django.contrib.auth.models import User
from accounts.serializers import UserProfileSerializer
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q
from django.http import Http404
from .models import FriendRequest
from .serializers import FriendRequestSerializer
from accounts.serializers import UserProfileDetailsSerializer
# Create your views here.


class userSearchAPIViews(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        keyword = request.query_params.get('keyword', '')

        if keyword:
            if registrationView.validate_email_formate(keyword):
                try:
                    user_data = User.objects.get(email=keyword)
                except User.DoesNotExist:
                    raise Http404
                user_serializer = UserProfileSerializer(user_data)
                return Response({"result": user_serializer.data}, status=status.HTTP_200_OK)
            else:
                users = User.objects.filter(
                    Q(username__icontains=keyword) | 
                    Q(first_name__icontains=keyword)
                ).order_by('id')
                paginator = PageNumberPagination()
                paginator.page_size = 10
                result_page = paginator.paginate_queryset(users, request)
                if not result_page:
                    return Response({"detail": "Invalid page."}, status=status.HTTP_404_NOT_FOUND)
                serializer = UserProfileSerializer(result_page, many=True)
                return paginator.get_paginated_response(serializer.data)
        else:
            return Response({"result": "Not Found"}, status=status.HTTP_200_OK)
        

class SendFriendRequestApiView(APIView):
    permission_classes = [IsAuthenticated]
    @staticmethod
    def get_obj(id):
        try:
            return User.objects.get(id=id)
        except:
            raise Http404

    def post(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        to_user = self.get_obj(to_user_id)
        from_user = request.user

        if from_user == to_user:
            return Response({'error': 'You cannot send a friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        request_id = request.data.get('request_id')
        friend_request = FriendRequest.objects.get(id=request_id)

        if friend_request.to_user != request.user:
            return Response({'error': 'You are not authorized to accept this friend request'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.accepted = True
        friend_request.save()
        return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
    

class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        accepted_requests = FriendRequest.objects.filter(to_user=user, accepted=True)
        friends = [friend_request.from_user for friend_request in accepted_requests]
        serializer = UserProfileSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PendingFriendRequestsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(to_user=user, accepted=False)
        pending_friends = [request.from_user for request in pending_requests]
        serializer = UserProfileSerializer(pending_friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
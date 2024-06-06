from django.contrib.auth.models import User
from rest_framework import serializers
from feature.models import FriendRequest
from feature.serializers import *
from django.db.models import Q

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'password', 'email', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileCurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class UserProfileDetailsSerializer(serializers.ModelSerializer):
    sent_requests = serializers.SerializerMethodField()
    received_requests = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'sent_requests', 'received_requests', 'friends']

    def get_sent_requests(self, obj):
        sent_requests = FriendRequest.objects.filter(from_user=obj, accepted=False)
        return FriendRequestSerializer(sent_requests, many=True).data

    def get_received_requests(self, obj):
        received_requests = FriendRequest.objects.filter(to_user=obj, accepted=False)
        return FriendRequestSerializer(received_requests, many=True).data

    def get_friends(self, obj):
        friends = User.objects.filter(
            Q(sent_requests__to_user=obj, sent_requests__accepted=True) |
            Q(received_requests__from_user=obj, received_requests__accepted=True)
        ).distinct()
        return UserProfileCurrentUserSerializer(friends, many=True).data
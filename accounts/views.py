from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer, UserProfileSerializer, UserProfileDetailsSerializer
from django.db import IntegrityError
import re

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from rest_framework.permissions import AllowAny, IsAuthenticated



class registrationView(APIView):
    permission_classes = [AllowAny]
    @staticmethod
    def validate_email_formate(email:str)->bool:
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)
    
    def post(self, request):
        if not self.validate_email_formate(request.data['email']):
            return Response({"error": "Email Invalid"}, status=status.HTTP_400_BAD_REQUEST)

        user_serilizer = UserSerializer(data=request.data)
        try:
            if user_serilizer.is_valid():
                user_serilizer.save()
                return Response({'Message': "Registration Succesfully!"}, status=status.HTTP_201_CREATED)
            return Response({'error' : user_serilizer.errors}, status = status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response({'error': 'User is alredy Registered!'})
        except Exception as e:
            return Response({'error' : str(e)}, status = status.HTTP_400_BAD_REQUEST)
        

class loginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"id":user.id,"user" : user.email,'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileDetailsSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

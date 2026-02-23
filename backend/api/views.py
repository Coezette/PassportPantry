from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.db.models import Sum
# Restframework
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# Utilities
from datetime import datetime
import json
import random

# Local Imports
from api import serializers as api_serializers
from api import models as api_models

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializers.MyTokenObtainPairSerializer
    
class RegisterView(generics.CreateAPIView):
    queryset = api_models.User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RegisterSerializer
    
class UserProfileView(generics.RetrieveUpdateAPIView):
    # queryset = api_models.UserProfile.objects.all()
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    serializer_class = api_serializers.UserProfileSerializer
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return user.userprofile


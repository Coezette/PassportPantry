from django.shortcuts import render, get_object_or_404
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
from rest_framework import status as response_status
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
    # permission_classes = [AllowAny]
    serializer_class = api_serializers.MyTokenObtainPairSerializer
    
class RegisterView(generics.CreateAPIView):
    queryset = api_models.User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RegisterSerializer
    
class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializers.UserSerializer
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        
        otp = payload['otp']
        uidb64 = payload['uidb64']
        password = payload['password']

        

        user = api_models.User.objects.get(id=uidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()
            
            return Response( {"message": "Password Changed Successfully"}, status=response_status.HTTP_201_CREATED)
        else:
            return Response( {"message": "An Error Occured"}, status=response_status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
def generate_numeric_otp(length=7):
        otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        return otp

class PasswordEmailVerify(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = api_serializers.UserSerializer
    
    def get_object(self):
        email = self.kwargs['email']
        user = api_models.User.objects.get(email=email)
        
        if user:
            user.otp = generate_numeric_otp()
            uidb64 = user.pk
            
            refresh = RefreshToken.for_user(user)
            reset_token = str(refresh.access_token)

            user.reset_token = reset_token
            user.save()

            link = f"http://localhost:5173/create-new-password?otp={user.otp}&uidb64={uidb64}&reset_token={reset_token}"
            
            merge_data = {
                'link': link, 
                'username': user.username, 
            }
            subject = f"Password Reset Request"
            text_body = render_to_string("email/password_reset.txt", merge_data)
            html_body = render_to_string("email/password_reset.html", merge_data)
            
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[user.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        return user
class UserProfileView(generics.RetrieveUpdateAPIView):
    # queryset = api_models.UserProfile.objects.all()
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    serializer_class = api_serializers.UserProfileSerializer
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return user.userprofile

class CountryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = api_models.Country.objects.all()
    serializer_class = api_serializers.CountrySerializer
    # def get_queryset(self):
    #     return super().get_queryset()
    
class CountryRecipeListView(generics.ListAPIView):
    # queryset = api_models.Recipe.objects.all()
    serializer_class = api_serializers.RecipeSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        country_id = self.kwargs['country_id']
        return api_models.Recipe.objects.filter(country__id=country_id, status='published').order_by('-created_at')
    
class RecipeListView(generics.ListAPIView):
    queryset = api_models.Recipe.objects.all().filter(status='published').order_by('-created_at')
    serializer_class = api_serializers.RecipeSerializer
    permission_classes = [AllowAny]
    
class RecipeDetailView(generics.RetrieveAPIView):
    serializer_class = api_serializers.RecipeSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        slug = self.kwargs['slug']
        recipe = api_models.Recipe.objects.get(slug=slug, status='published')
        recipe.view_count += 1
        recipe.save()
        return recipe
    
class LikeRecipeView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data['user_id']
        recipe_id = request.data['recipe_id']
        
        user = api_models.User.objects.get(id=user_id)
        recipe = api_models.Recipe.objects.get(id=recipe_id)        
        
        if user in recipe.likes.all():
            recipe.likes.remove(user)
            return Response({'message': 'Recipe unliked'}, status=response_status.HTTP_200_OK)
        else:
            recipe.likes.add(user)
            api_models.Notification.objects.create(
                user=recipe.author,
                recipe=recipe,
                type='like',
            )
            return Response({'message': 'Recipe liked'}, status=response_status.HTTP_200_OK)

class RecipeCommentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        recipe_id = request.data['recipe_id']
        name = request.data['name']
        email = request.data['email']
        content = request.data['content']
        
        recipe = api_models.Recipe.objects.get(id=recipe_id)
        api_models.Comment.objects.create(
            recipe=recipe,
            name=name,
            content=content,
            email=email,
        )
        
        api_models.Notification.objects.create(
            user=recipe.author,
            recipe=recipe,
            type='comment',
        )
        
        return Response({'message': 'Comment added'}, status=response_status.HTTP_201_CREATED)
    
class PassportStampView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        user_id = request.data['user_id']
        recipe_id = request.data['recipe_id']
        county_id = request.data.get('country_id', None)
        
        user = api_models.User.objects.get(id=user_id)
        recipe = api_models.Recipe.objects.get(id=recipe_id)
        country = api_models.Country.objects.get(id=county_id) if county_id else None
        
        #check if passport stamp exists
        passport_stamp = api_models.PassportStamp.objects.filter(user=user, country=country).first()
        if passport_stamp:
            passport_stamp.delete()
            return Response({'message': 'Country stamp removed'}, status=response_status.HTTP_200_OK)
        else:
            api_models.PassportStamp.objects.create(user=user, country=country, stamped_at=datetime.now())
            
            api_models.Notification.objects.create(
                user=recipe.author,
                recipe=recipe,
                type='stamp',
            )
            return Response({'message': 'Country stamp added'}, status=response_status.HTTP_201_CREATED)
        
#>>>>>>>>>>>Author Dashboard Stats Views>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class DashboardStatsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.AuthorStatisticsSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        
        total_views = api_models.Recipe.objects.filter(author=user).aggregate(views=Sum('view_count'))['views']
        total_recipes = api_models.Recipe.objects.filter(author=user).count()
        total_likes = api_models.Recipe.objects.filter(author=user).aggregate(likes=Sum('likes'))['likes']
        passport_stamps = api_models.PassportStamp.objects.filter(user=user).count()
        
        return [
            {
                'views': total_views,
                'likes': total_likes,
                'recipes': total_recipes,
                'stamps': passport_stamps
            }
        ]
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class DashboardRecipesListsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RecipeSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Recipe.objects.filter(author=user).order_by('-created_at')
    
class DashboardCommentsListsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.CommentSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Comment.objects.filter(recipe__author=user).order_by('-created_at')
    
class DashboardStampsListsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.PassportStampSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.PassportStamp.objects.filter(user=user).order_by('-stamped_at')
    
class DashboardNotificationsListsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.NotificationSerializer
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = api_models.User.objects.get(id=user_id)
        return api_models.Notification.objects.filter(user=user, seen=False).order_by('-created_at')
    
class MarkNotificationAsReadView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        notification_id = request.data['notification_id']
        notification = api_models.Notification.objects.get(id=notification_id)
        notification.seen = True
        notification.save()
        return Response({'message': 'Notification marked as read'}, status=response_status.HTTP_200_OK)
    
class ReplyCommentView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        comment_id = request.data['comment_id']
        reply = request.data['reply']
        
        parent_comment = api_models.Comment.objects.get(id=comment_id)
        parent_comment.reply = reply
        parent_comment.save()
        
        return Response({'message': 'Reply added'}, status=response_status.HTTP_201_CREATED)
    
    #>>>>>>>>>>Recipe Creation Views>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class CreateRecipeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RecipeSerializer
        
    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        country_id = request.data.get('country_id')
        title = request.data.get('title')
        description = request.data.get('description')
        ingredients = request.data.get('ingredients')
        instructions = request.data.get('instructions')
        prep_time_minutes = request.data.get('prep_time_minutes')
        cook_time_minutes = request.data.get('cook_time_minutes')
        servings = request.data.get('servings')
        difficulty = request.data.get('difficulty')
        cover_image = request.FILES.get('cover_image')
        status = request.data.get('status',)
        tags = request.data.get('tags')
            
        user = api_models.User.objects.get(id=user_id)
        country = api_models.Country.objects.get(id=country_id) if country_id else None
            
        api_models.Recipe.objects.create(
            author=user,
            country=country,
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            prep_time_minutes=prep_time_minutes,
            cook_time_minutes=cook_time_minutes,
            servings=servings,
            difficulty=difficulty,
            cover_image=cover_image,
            status=status,
            tags=tags,
        )
            
        return Response({'message': 'Recipe created successfully'}, status=response_status.HTTP_201_CREATED)
            
class RecipeUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializers.RecipeSerializer
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        recipe_id = self.kwargs['recipe_id']
        
        user = api_models.User.objects.get(id=user_id)
        return api_models.Recipe.objects.get(id=recipe_id, author=user)
    
    def update(self, request, *args, **kwargs):
        recipe_instance = self.get_object()
        
        country_id = request.data.get('country_id')
        title = request.data.get('title')
        description = request.data.get('description')
        ingredients = request.data.get('ingredients')
        instructions = request.data.get('instructions')
        prep_time_minutes = request.data.get('prep_time_minutes')
        cook_time_minutes = request.data.get('cook_time_minutes')
        servings = request.data.get('servings')
        difficulty = request.data.get('difficulty')
        cover_image = request.FILES.get('cover_image')
        status = request.data.get('status', 'published')
        tags = request.data.get('tags')

        country = api_models.Country.objects.get(id=country_id) if country_id else None
        recipe_instance.country = country
        recipe_instance.title = title
        recipe_instance.description = description
        recipe_instance.ingredients = ingredients
        recipe_instance.instructions = instructions
        recipe_instance.prep_time_minutes = prep_time_minutes
        recipe_instance.cook_time_minutes = cook_time_minutes
        recipe_instance.servings = servings
        recipe_instance.difficulty = difficulty
        
        if cover_image:
            recipe_instance.cover_image = cover_image

        recipe_instance.status = status
        recipe_instance.tags = tags
        recipe_instance.save()
        
        return Response({'message': 'Recipe updated successfully'}, status=response_status.HTTP_200_OK)

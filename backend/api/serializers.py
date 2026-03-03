from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from api import models as api_models

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = api_models.User
        fields = ('username', 'email', 'full_name', 'password', 'password2')
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords didn't match."})
        return attrs
        
    def create(self, validated_data):
        # full_name is optional; default will be set in User.save() if empty
        user = api_models.User.objects.create(
            username=validated_data['username'],
            full_name=validated_data['full_name'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.User
        fields = "__all__"
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.UserProfile
        fields = "__all__"
        
class CountrySerializer(serializers.ModelSerializer):
    recipe_count = serializers.SerializerMethodField()
    def get_recipe_count(self, country):
        # return country.recipe.count()
        return country.recipe_count()
    
    class Meta:
        model = api_models.Country
        fields = ["id", "name", "iso_code", "recipe_count", "flag_emoji", "continent", "recipes"]
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Comment
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super(CommentSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Recipe
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super(RecipeSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

class PassportStampSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.PassportStamp
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super(PassportStampSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Notification
        fields = "__all__"
        
    def __init__(self, *args, **kwargs):
        super(NotificationSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.method == 'POST':
            self.Meta.depth = 0
        else:
            self.Meta.depth = 1

class AuthorStatisticsSerializer(serializers.Serializer):
    views = serializers.IntegerField(default=0)
    likes = serializers.IntegerField(default=0)
    recipes = serializers.IntegerField(default=0)
    stamps_issued = serializers.IntegerField(default=0)
    
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    display_name = models.CharField(max_length=100, blank=True)
    home_country = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.user.username
    
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=2, unique=True)
    flag_imoji = models.CharField(max_length=10, blank=True)
    continent = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name
    
class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField()
    instructions = models.TextField()
    prep_time_minutes = models.IntegerField(null=True, blank=True)
    cook_time_minutes = models.IntegerField(null=True, blank=True)
    servings = models.IntegerField(null=True, blank=True)
    difficulty = models.CharField(max_length=50, blank=True) #choice?
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    indexes = [
        models.Index(fields=['country']),
        models.Index(fields=['is_published']),
    ]
    
class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='recipe_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    ordering = ['order', 'uploaded_at']
    
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    
    unique_together = ('user', 'recipe')
    
class PassportStamp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passport_stamps')
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    stamped_at = models.DateTimeField(auto_now_add=True)
    
    unique_together = ('user', 'country')
    
    indexes = [
        models.Index(fields=['user']),
    ]
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
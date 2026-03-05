from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.text import slugify

class User(AbstractUser):
    username = models.CharField(max_length=200, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def save(self, *args, **kwargs):
        email_username, domain = self.email.split('@')
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username
        super(User, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.full_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    avatar = models.FileField(upload_to='images/', null=True, blank=True, default="default/default-user.jpg")
    bio = models.TextField(blank=True, max_length=500)
    username = models.CharField(max_length=200, unique=True)
    full_name = models.CharField(max_length=200, blank=True, null=True)
    home_country = models.CharField(max_length=100, blank=True, null=True)
    author = models.BooleanField(default=False)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        if self.username == "" or self.username == None:
            self.username = self.user.username

        super(UserProfile, self).save(*args, **kwargs)
        
#signals to create and save user profile when user is created or saved
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
    
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
    
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    iso_code = models.CharField(max_length=2, unique=True)
    flag_emoji = models.CharField(max_length=50, blank=True, null=True)
    continent = models.CharField(max_length=50, blank=True, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True)

    
    class Meta:
        verbose_name_plural = "Countries"
    
    def recipe_count(self):
        return Recipe.objects.filter(country=self).count()
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name)
        super(Country, self).save(*args, **kwargs)
    
class Recipe(models.Model):
    STATUS_CHOICES = (
        ('draft', 'draft'),
        ('published', 'published'),
        ('archived', 'archived'),
    )
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipes', null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ingredients = models.TextField()
    instructions = models.TextField()
    prep_time_minutes = models.IntegerField(null=True, blank=True)
    cook_time_minutes = models.IntegerField(null=True, blank=True)
    servings = models.IntegerField(null=True, blank=True)
    difficulty = models.CharField(max_length=50, blank=True) #choice?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cover_image = models.FileField(upload_to='images/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    view_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, null=True, blank=True, related_name='liked_recipes')
    tags = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title)
        super(Recipe, self).save(*args, **kwargs)
        
    def total_likes(self):
        return self.likes.count()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Recipes"
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['status']),
        ]
    
class PassportStamp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='passport_stamps')
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    stamped_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.country.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'country'], name='unique_user_country_stamp')
        ]
        verbose_name_plural = "Passport Stamps"
    
class Comment(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.recipe.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Comments"
        
class Notification(models.Model):
    NOTIFICATIONS_TYPES = (
        ('like', 'like'),
        ('comment', 'comment'),
        ('stamp', 'stamp'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=NOTIFICATIONS_TYPES)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.recipe:
            return f"{self.type} notification for {self.recipe.title}"
        else:
            return f"{self.type} notification"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notifications"
        
    
# class RecipeImage(models.Model):
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
#     image = models.FileField(upload_to='recipe_images/')
#     caption = models.CharField(max_length=200, blank=True)
#     is_cover = models.BooleanField(default=False)
#     order = models.IntegerField(default=0)
#     uploaded_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['order', 'uploaded_at']
    
# class Tag(models.Model):
#     name = models.CharField(max_length=50, unique=True)
#     slug = models.SlugField(max_length=50, unique=True)
    
#     def __str__(self):
#         return self.name

# class Like(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
#     created_at=models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['user', 'recipe'], name='unique_user_recipe_like')
#         ]
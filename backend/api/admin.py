from django.contrib import admin

from api import models as api_models

class RecipeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    
class CountryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['name']}

admin.site.register(api_models.User)
admin.site.register(api_models.UserProfile)
admin.site.register(api_models.Country, CountryAdmin)
admin.site.register(api_models.Recipe, RecipeAdmin)
admin.site.register(api_models.PassportStamp)
admin.site.register(api_models.Comment)
admin.site.register(api_models.Notification)
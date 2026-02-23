from django.contrib import admin

from api import models as api_models

admin.site.register(api_models.User)
admin.site.register(api_models.UserProfile)
admin.site.register(api_models.Country)
admin.site.register(api_models.Recipe)
admin.site.register(api_models.PassportStamp)
admin.site.register(api_models.Comment)
admin.site.register(api_models.Notification)
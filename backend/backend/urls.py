from django.contrib import admin
from django.urls import include, path
# from api.views import UserCreate
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]

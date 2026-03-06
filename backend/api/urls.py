from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from api import views as api_views

urlpatterns = [
    path('user/token/', api_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', api_views.RegisterView.as_view(), name='register'),
    path('user/password-reset/<email>/', api_views.PasswordEmailVerify.as_view(), name='password_reset'),
    path('user/password-change/', api_views.PasswordChangeView.as_view(), name='password_reset'),
    path('user/profile/<int:user_id>/', api_views.UserProfileView.as_view(), name='user-profile'),
    path('countries/', api_views.CountryListView.as_view(), name='country-list'),
    path('countries/<int:country_id>/recipes/', api_views.CountryRecipeListView.as_view(), name='country-recipes'),
    path('recipes/', api_views.RecipeListView.as_view(), name='recipe-list'),
    path('recipes/detail/<slug>/', api_views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('recipes/like-recipe/', api_views.LikeRecipeView.as_view(), name='recipe-like'),
    path('recipes/comment-recipe/', api_views.RecipeCommentView.as_view(), name='recipe-comment'),
    path('recipes/passport-stamp/', api_views.PassportStampView.as_view(), name='passport-stamp'),
    path('author/dashboard/stats/<int:user_id>/', api_views.DashboardStatsView.as_view(), name='author-dashboard'),
    path('dashboard/recipes/<int:user_id>/', api_views.DashboardRecipesListsView.as_view(), name='author-recipes'),
    path('dashboard/comments/<int:user_id>/', api_views.DashboardCommentsListsView.as_view(), name='author-comments'),
    path('dashboard/stamps/<int:user_id>/', api_views.DashboardStampsListsView.as_view(), name='author-stamps'),
    path('dashboard/notifications/<int:user_id>/', api_views.DashboardNotificationsListsView.as_view(), name='author-notifications'),
    path('dashboard/notifications/mark-read/<int:notification_id>/', api_views.MarkNotificationAsReadView.as_view(), name='mark-notification-read'),
    path('dashboard/comments/reply/', api_views.ReplyCommentView.as_view(), name='comment-reply'),
    path('recipes/create/', api_views.CreateRecipeView.as_view(), name='create-recipe'),
    path('recipes/update/<int:recipe_id>/<int:user_id>/', api_views.RecipeUpdateView.as_view(), name='update-recipe'),
    # path('recipes/delete/<slug>/', api_views.DeleteRecipeView.as_view
]
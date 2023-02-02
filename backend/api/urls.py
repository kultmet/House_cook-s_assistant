from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views.cuisine_views import RecipeVievSet, TagViewSet
from api.views.users_views import FollowViewSet, followings, Followings

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeVievSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
# router.register(r'users', FollowViewSet, basename='subscriptions')# (?P<id>\d+)


urlpatterns = [
    path('', include(router.urls)),
    # path('users/subscriptions/', followings, name='subscriptions'),# subscriptions/
    path('users/subscriptions/', Followings.as_view(), name='subscriptions'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
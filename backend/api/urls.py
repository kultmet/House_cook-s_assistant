from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.views.cuisine_views import RecipeVievSet, TagViewSet, BaseIngredientViewSet, FavoriteViewSet, favorite, order#, download_order
from api.views.users_views import FollowViewSet, followings, Followings

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeVievSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', BaseIngredientViewSet, basename='ingredients')
# router.register(
#     r'recipes/(?P<id>\d+)/favorite',
#     FavoriteViewSet,
#     basename='favorite'
# )
# router.register(r'users', FollowViewSet, basename='subscriptions')# (?P<id>\d+)


urlpatterns = [
    path('', include(router.urls)),
    # path('users/subscriptions/', followings, name='subscriptions'),# subscriptions/
    # path('users/subscriptions/', Followings.as_view(), name='subscriptions'),
    path('recipes/<id>/favorite/', favorite, name='favorite'),
    path('recipes/<id>/shopping_cart/', order, name='shopping_cart'),
    # path('recipes/download_shopping_cart/', download_order, name='download_shopping_cart'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
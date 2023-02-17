from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.cuisine_views import (
    RecipeVievSet, TagViewSet, BaseIngredientViewSet, favorite, order
)
from api.views.users_views import CustomUserViewSet

app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeVievSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', BaseIngredientViewSet, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<id>/favorite/', favorite, name='favorite'),
    path('recipes/<id>/shopping_cart/', order, name='shopping_cart'),
    path('auth/', include('djoser.urls.authtoken')),
]

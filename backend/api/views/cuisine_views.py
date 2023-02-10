import os
from pathlib import Path
from datetime import date

from django.http import HttpResponse
from django.conf import settings
from django.db.models import Sum, Count
from django_filters import rest_framework as filters
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, validators
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from cuisine.models import Recipe, Tag, BaseIngredientWithUnits, Favorite, Order, IngredientRecipe
from api.serializers.cuisine_serializers import (
    TagSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    BaseIngredientSerializer,
    FavoriteSerializer,
    OrderSerializer
)
from api.views.generators import txt_generator
from api.filters.filters import RecipeFilterSet
from api.paginators import CustomPaginator


class BaseIngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для Базового Ингредиента."""
    queryset = BaseIngredientWithUnits.objects.all()
    serializer_class = BaseIngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для Тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeVievSet(ModelViewSet):
    """ViewSet для Рецепта."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginator
    # pagi = (PageNumberPagination,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(
            methods=['get', ],
            url_path='download_shopping_cart',
            queryset=Order.objects.all(),
            detail=False,
            permission_classes = (IsAuthenticated,)
    )
    def download_order(self, request):
        """Сохраняем файл со списком Покупок."""
        user = request.user
        # my_orders = user.orders.select_related('recipe')
        # recipes = Recipe.objects.filter(orders__user=user)
        ingredients = IngredientRecipe.objects.filter(
            recipe__orders__user=user
        )
        calculation_results = ingredients.values(
            'base_ingredient__name',
            'base_ingredient__measurement_unit'
        ).annotate(Sum('amount')).order_by()
        filename = f'{request.user.username}_{date.today()}.txt'
        file_adrass = Path(os.path.join(settings.ORDERS_ROOT, filename))
        result = txt_generator(calculation_results, file_adrass)
        response = HttpResponse(
                result,
                content_type='text/txt',
            )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
        # print(ingredients.annotate(Sum('amount')), 'annotate')
        # calculation_results = {}
        # for i in ingredients.values('base_ingredient__name').distinct():
        #     print(i.keys(), i.values())
        # # print(my_orders)
        # print(recipes)
        # print(ingredients)
        
        # return Response(calculation_results)
        
            # filename = f'{request.user.username}_{date.today()}.txt'
            # file_adrass = Path(os.path.join(settings.ORDERS_ROOT, filename))
            # txt_generator(calculation_results, file_adrass)
            # file = open(file_adrass, 'r', encoding='UTF-8').read()
            

@api_view(http_method_names=['POST', 'DELETE'])
def favorite(request, id):
    """Добавляет рецепт в Избранное. Удаляет из Избранного."""
    data = {}
    data['request'] = request
    data['recipe_id'] = id
    if request.method == 'POST':
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = FavoriteSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    recipe = serializer.validated_data['recipe']
    favorite_recipe = get_object_or_404(Favorite, user=user, recipe=recipe)
    favorite_recipe.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(http_method_names=['POST', 'DELETE'])# Еще метод get
def order(request, id):
    """Добавляет в Корзину Покупок. Удаляет из Корзину Покупок."""
    data = {}
    data['request'] = request
    data['recipe_id'] = id
    if request.method == 'POST':
        serializer = OrderSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    serializer = OrderSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    recipe = serializer.validated_data['recipe']
    order = get_object_or_404(Order, user=user, recipe=recipe)
    order.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)

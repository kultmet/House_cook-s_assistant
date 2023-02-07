from pathlib import Path
from django.shortcuts import render
from django.db.models import Sum, Max, Count
from django.http import HttpResponse
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.renderers import BaseRenderer
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
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
# from api.views.generators import ingredients_output_generator

class BaseIngredientViewSet(ReadOnlyModelViewSet):
    queryset = BaseIngredientWithUnits.objects.all()
    serializer_class = BaseIngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):#ListModelMixin, RetrieveModelMixin, GenericViewSet
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeVievSet(ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(methods=['get', ], url_path='download_shopping_cart', queryset=Order.objects.all(), detail=False)
    def download_order(self, request):
        user = request.user
        # orders = Order.objects.filter(user=request.user)#.annotate('recipe')#.annotate(Count('recipe'))
        my_orders = user.orders.select_related('recipe')
        calculation_results = {}
        for order in my_orders:
            recipe = Recipe.objects.get(id=order.recipe.id)
            ingredients = IngredientRecipe.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                inner = {}
                if ingredient.base_ingredient.name in calculation_results:
                    calculation_results[ingredient.base_ingredient.name]['amount'] += ingredient.amount
                else:
                    inner['name'] = ingredient.base_ingredient.name
                    inner['amount'] = ingredient.amount
                    inner['measurement_unit'] = ingredient.base_ingredient.measurement_unit
                    calculation_results[ingredient.base_ingredient.name] = inner
            with open(Path(f'{request.user.username}_.txt'), 'w') as file:
                file.write('fuck')
            response = HttpResponse(f'{request.user.username}.txt', content_type='text/txt',)
            response['Content-Disposition'] = f'attachment; filename={Path(f"{request.user.username}.txt")}'
            return response
            # response = FileResponse(open(Path(f'{request.user.username}.txt'), 'w'))
            # # response
            # print(response)
        # return response#Response({'message': calculation_results})
        
    

@api_view(http_method_names=['POST', 'DELETE'])# Сделать функцию не могу передать context['view']
def favorite(request, id):
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

# class 

# @api_view(http_method_names=['GET',])   




class FavoriteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        print('destroy сработал')
        return super().destroy(request, *args, **kwargs)
    
    def perform_destroy(self, instance):
        print('perform_destroy сработал')
        return super().perform_destroy(instance)


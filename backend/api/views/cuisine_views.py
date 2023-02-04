from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from cuisine.models import Recipe, Tag, BaseIngredientWithUnits
from api.serializers.cuisine_serializers import TagSerializer, RecipeSerializer, CreateRecipeSerializer, BaseIngredientSerializer


class BaseIngredientViewSet(ReadOnlyModelViewSet):
    queryset = BaseIngredientWithUnits.objects.all()
    serializer_class = BaseIngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):#ListModelMixin, RetrieveModelMixin, GenericViewSet
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeVievSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return CreateRecipeSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def create(self, request, *args, **kwargs):

    #     # for i in range(len(request.data['tags'])):
    #     #     request.data['tags'][i] = {'id': request.data['tags'][i]}
    #     # print(request.data['tags'])
    #     return super().create(request, *args, **kwargs)

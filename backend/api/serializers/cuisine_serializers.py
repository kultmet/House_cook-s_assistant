# from io import BytesIO, StringIO
import uuid
import base64
from PIL import Image

import webcolors
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.core.files.base import ContentFile
from cuisine.models import Recipe, Tag, IngredientRecipe, BaseIngredientWithUnits, Favorite, Order, TagRecipe
from users.models import Follow
from api.serializers.users_serializers import UserSerializer

# Coral	#FF7F50 завтрак
# MediumSeaGreen	#3CB371 обед
# BlueViolet	#8A2BE2  ужин
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class TagRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True, source='tag.id')
    name = serializers.StringRelatedField(read_only=True, source='tag.name')
    color = serializers.StringRelatedField(read_only=True, source='tag.color')
    slug = serializers.StringRelatedField(read_only=True, source='tag.slug')
    class Meta:
        model = TagRecipe
        # model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(
        read_only=True, source='base_ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        read_only=True, source='base_ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        source='base_ingredient.id'
    )
    
    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'amount',
            'measurement_unit',
        )


class BaseIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)
    class Meta:
        model = BaseIngredientWithUnits
        fields = (
            'id',
            'amount',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'name',
            'measurement_unit',
        )


class Base64ToImageField(serializers.ImageField):
    """Поле картинки."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}'
            )
        return super().to_internal_value(data)


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = BaseIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())#
    image = Base64ToImageField()
    text = serializers.CharField(source='description')
    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
    
    def to_representation(self, instance):
        return RecipeSerializer(instance=instance, context=self.context).data
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=recipe)
        for ingredient in ingredients:
            base_ingredient = get_object_or_404(
                BaseIngredientWithUnits,
                id=ingredient['id']
            )
            IngredientRecipe.objects.create(
                base_ingredient=base_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True, source='ingredientrecipe')
    tags = TagRecipeSerializer(many=True, source='tagrecipe', read_only=True)
    text = serializers.CharField(source='description')
    image = Base64ToImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()
    
    def get_is_in_shopping_cart(self, obj):
        return Order.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        fields = ('author', 'recipes',)
        model = Follow
    
    def validate_following(self, value):
        if value == self._context['request'].user:
            raise serializers.ValidationError(
                "На себя подписываться безсмысленно!"
            )
        return value
